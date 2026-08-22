// Kopiert die Stammdaten aus dem Repo-Verzeichnis /data nach web/public/data,
// damit die statische Angular-App sie als Assets ausliefern kann.
// Single Source of Truth bleibt /data; public/data ist ein Build-Artefakt (gitignored).
import {
  readdirSync, mkdirSync, copyFileSync, existsSync, readFileSync, writeFileSync, rmSync,
} from 'node:fs';
import { dirname, join, extname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, '..', '..', 'data');
const dest = join(here, '..', 'public', 'data');

mkdirSync(dest, { recursive: true });
const files = readdirSync(src).filter((f) => f.endsWith('.json'));
for (const f of files) {
  copyFileSync(join(src, f), join(dest, f));
}
console.log(`sync-data: ${files.length} Dateien nach public/data kopiert.`);

// US-024: Komponisten-Portraits nach public/portraits spiegeln (Build-Artefakt, gitignored).
// Single Source of Truth bleibt data/portraits; die App bindet lokale Dateien unter
// `portraits/<file>` ein und ruft keine Fremd-URLs zur Laufzeit ab.
//
// Optimierung (Performance auf Mobilgeräten): Die Originale sind teils extrem groß
// (einzelne PNG-Fotos > 1,9 MB). Beim Spiegeln werden die Bilder daher auf eine
// sinnvolle Anzeigebreite (max. 480px – deckt Liste 200px und Detail 352px inkl.
// Retina ab) skaliert und als komprimiertes JPEG neu kodiert. PNG-/GIF-Fotos werden
// dabei zu .jpg; die Referenzen in public/data/composers.json (Build-Artefakt) werden
// entsprechend angepasst, damit die App die optimierten Dateien lädt.
const PORTRAIT_MAX_WIDTH = 480;
const PORTRAIT_JPEG_QUALITY = 82;

const portraitsSrc = join(here, '..', '..', 'data', 'portraits');
const portraitsDest = join(here, '..', 'public', 'portraits');

/** Ordnet den Original-Dateinamen (wie in composers.json referenziert) den optimierten zu. */
const portraitRename = new Map();

if (existsSync(portraitsSrc)) {
  // Zielordner säubern, damit keine veralteten (z. B. nicht mehr referenzierten
  // PNG/GIF-)Dateien früherer Läufe im Build-Artefakt zurückbleiben.
  rmSync(portraitsDest, { recursive: true, force: true });
  mkdirSync(portraitsDest, { recursive: true });
  const images = readdirSync(portraitsSrc).filter((f) => !f.startsWith('.'));

  // Einfache Nebenläufigkeit, damit die Skalierung von ~225 Bildern zügig läuft.
  const CONCURRENCY = 8;
  let cursor = 0;
  let optimized = 0;
  let copiedFallback = 0;

  const worker = async () => {
    while (cursor < images.length) {
      const file = images[cursor++];
      const inPath = join(portraitsSrc, file);
      const outName = `${basename(file, extname(file))}.jpg`;
      try {
        await sharp(inPath)
          .resize({ width: PORTRAIT_MAX_WIDTH, withoutEnlargement: true })
          .flatten({ background: '#ffffff' })
          .jpeg({ quality: PORTRAIT_JPEG_QUALITY, progressive: true, mozjpeg: true })
          .toFile(join(portraitsDest, outName));
        portraitRename.set(file, outName);
        optimized++;
      } catch (err) {
        // Fallback: Original unverändert kopieren, Referenz unverändert lassen.
        copyFileSync(inPath, join(portraitsDest, file));
        portraitRename.set(file, file);
        copiedFallback++;
        console.warn(`sync-data: Portrait ${file} nicht optimierbar (${err.message}), Original kopiert.`);
      }
    }
  };

  await Promise.all(Array.from({ length: CONCURRENCY }, worker));
  console.log(
    `sync-data: ${optimized} Portraits optimiert, ${copiedFallback} als Original kopiert (public/portraits).`,
  );

  // Referenzen im Build-Artefakt composers.json auf die optimierten Dateinamen umbiegen.
  const composersPath = join(dest, 'composers.json');
  if (existsSync(composersPath)) {
    const data = JSON.parse(readFileSync(composersPath, 'utf8'));
    let patched = 0;
    for (const composer of data.composers ?? []) {
      const current = composer.portrait?.file;
      if (!current) continue;
      const next = portraitRename.get(current);
      if (next && next !== current) {
        composer.portrait.file = next;
        patched++;
      }
    }
    writeFileSync(composersPath, JSON.stringify(data));
    console.log(`sync-data: ${patched} Portrait-Referenzen in composers.json angepasst.`);
  }
}
