# ADR-004: Angular und TypeScript als Frontend-Framework

**Status:** accepted (2026-08-18)

## Evaluation criteria

**Summary:** Gesucht ist der Frontend-Stack für die statische Webapp
([ADR-001](ADR-001-statische-webapp-ohne-backend.md)). Der Kern ist eine
Kalenderoberfläche mit Deep-Link-Routing, Detailseiten und rein lesendem Datenzugriff.

**Specifics:**

- **Statisch deploybar:** vollständiger Prerender-/Bundle-Build ohne Laufzeitserver.
- **Routing/Deep-Links:** Routen für Monate, Ensembles, Venues und Events (PRD §23).
- **Struktur & Erweiterbarkeit:** klare Komponenten-/Service-Struktur für spätere
  Filter/Karten.
- **Typsicherheit:** typisiertes Datenmodell passend zu den JSON-Entitäten.
- **Accessibility:** semantisches HTML, Tastaturbedienung, Fokuszustände (PRD §26).
- **Performance:** Lazy Loading, JSON nur einmal laden (PRD §29).

## Candidates to consider

**Summary:** Betrachtet werden die etablierten SPA-Frameworks, die statisch baubar sind.

1. **Angular + TypeScript** (Angular CLI).
2. **React** (+ Router, Build-Tool nach Wahl).
3. **Vue** (+ Vue Router).
4. **Svelte/SvelteKit** (static adapter).

## Research and analysis of each candidate

**Angular + TypeScript**

- Erfüllt alle Kriterien: Angular CLI baut ein rein statisches Bundle; Router mit
  `loadComponent` liefert Deep-Links und Lazy Loading; TypeScript erzwingt ein typisiertes
  Modell; Signals + `provideAppInitializer` decken das Einmal-Laden der Daten sauber ab.
- Cost: größere Framework-Grundlast und steilere Lernkurve als schlanke Alternativen;
  dafür „Batteries included" (Router, HttpClient, DI, Forms) ohne Zusatzentscheidungen.
- SWOT: **S** klare Konventionen, integriertes Routing/DI, gute Eignung für strukturierte
  UIs, langfristig stabil. **W** größeres Baseline-Bundle. **O** wächst mit
  Filter/Karten mit. **T** Major-Upgrades des Frameworks.

**React**

- Erfüllt die Kriterien technisch ebenfalls, erfordert aber mehr Einzelentscheidungen
  (Router, Datenzugriff, Struktur). Weniger vorgegebene Konventionen.

**Vue**

- Solider, schlanker Kandidat mit gutem Routing; im Team/PRD nicht priorisiert.

**Svelte/SvelteKit**

- Kleinste Bundles, aber kleineres Ökosystem; für die vorgesehene Struktur nicht nötig.

**Opinions/feedback:** PRD §22 empfiehlt Angular explizit („gute Unterstützung für
Kalenderoberflächen, klare Struktur, statisch deploybar"). Die Umsetzung nutzt Angular 20
mit Standalone-Komponenten, Signals und lazy geladenen Seiten – die Entscheidung ist bereits
implementiert.

## Recommendation

**Summary:** Angular 20 + TypeScript, gebaut mit der Angular CLI.

**Specifics:** Standalone-Komponenten, Signals als State-Primitive, `@angular/router` mit
`loadComponent` für Lazy-geladene Seiten, `HttpClient` für den lesenden JSON-Zugriff. Das
Datenmodell wird in `src/app/models/models.ts` typisiert und spiegelt die Entitätsdokus. Die
zentrale Datenzugriffsschicht ist der `DataService`
([ADR-006](ADR-006-datensync-als-build-artefakt.md) beschreibt die Datenbereitstellung).
Styling bleibt bewusst schlicht (CSS, PRD §28).
