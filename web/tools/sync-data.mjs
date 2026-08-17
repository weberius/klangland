// Kopiert die Stammdaten aus dem Repo-Verzeichnis /data nach web/public/data,
// damit die statische Angular-App sie als Assets ausliefern kann.
// Single Source of Truth bleibt /data; public/data ist ein Build-Artefakt (gitignored).
import { readdirSync, mkdirSync, copyFileSync } from 'node:fs';
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
