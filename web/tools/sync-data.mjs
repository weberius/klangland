// Kopiert die Stammdaten aus dem Repo-Verzeichnis /data nach web/public/data,
// damit die statische Angular-App sie als Assets ausliefern kann.
// Single Source of Truth bleibt /data; public/data ist ein Build-Artefakt (gitignored).
import { readdirSync, mkdirSync, copyFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

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
const portraitsSrc = join(here, '..', '..', 'data', 'portraits');
const portraitsDest = join(here, '..', 'public', 'portraits');
if (existsSync(portraitsSrc)) {
  mkdirSync(portraitsDest, { recursive: true });
  const images = readdirSync(portraitsSrc).filter((f) => !f.startsWith('.'));
  for (const f of images) {
    copyFileSync(join(portraitsSrc, f), join(portraitsDest, f));
  }
  console.log(`sync-data: ${images.length} Portraits nach public/portraits kopiert.`);
}
