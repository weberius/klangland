# Duisburger Philharmoniker – Ingest 2026/27

Quelle: [Konzertkalender](https://duisburger-philharmoniker.de/konzertkalender/) (WordPress)
+ Detailseiten `https://duisburger-philharmoniker.de/Konzerte/<slug>/`.

Skript: [`ingest_duisburg.py`](ingest_duisburg.py)

## Quelle / Technik

- Die **Kalenderseite** listet alle Konzert-Detail-Links (`/Konzerte/<slug>/`).
- Auf den **Detailseiten** stehen strukturiert:
  - Besetzung in `p.dpInterpreten` (`<strong>Name</strong> Rolle`; das Orchester als
    eigener Eintrag „Duisburger Philharmoniker");
  - Programm in `div.dpWerke` (`<strong>Komponist</strong><br>Werk`);
  - Termine in `dpInfos` („Mi. 25. / Do. 26. November 2026"), Beginn/Ort im Info-Widget;
  - Ticket-Links als `a.kartenLink` → Eventim-Inhouse (`theaterduisburg.eventim-inhouse.de/
    webshop/…?event=<id>`), je Aufführung mit Wochentag-Label („Karten Mi"/„Karten Do").

## Umfang / Filter

Aufgenommen werden nur Konzerte, bei denen die **Duisburger Philharmoniker** (bzw. deren
Mitglieder) auftreten – erkennbar an der Besetzung. Gast-Recitals und Fremdveranstaltungen
(viele Kammerkonzerte wie „Flamenco-Freiheit", Orgel-Recitals, reine Lied-/Ensembleabende)
werden ausgelassen (47 von 104 Detailseiten).

**Ortsprüfung:** Der Ort wird je Konzert aus dem `Ort`-Feld gelesen. Nur Konzerte in
**Duisburg** werden aufgenommen; **Auswärts-/Gastspiele** (Ort außerhalb Duisburgs, z. B.
Stadthalle Gütersloh, Konzert Theater Coesfeld) werden ausgelassen und **nicht** fälschlich
Duisburg zugeordnet. Ein Ort gilt als Duisburg, wenn er einer bekannten Duisburger Spielstätte
entspricht oder „Duisburg" enthält.

Ergebnis: **67 Aufführungen** aus 55 Produktionen (06.09.2026–30.07.2027). **46** haben einen
Ticketlink; **40** eine sichtbare Werkangabe (33 als strukturiertes `program[]`, 7 als
`description` „Werke von …"). 2 Auswärtskonzerte ausgelassen.

## Programm-Darstellung

- Enthält `dpWerke` eine Werkliste (`Komponist`/`Werk`), wird sie in `program[].workId`
  normalisiert (`works.json`/`composers.json` ergänzt; Genre heuristisch; Katalognummern
  op./KV/BWV/WoO/Hob/D geparst; `yearComposed`/`life`/`durationMinutes` `null`).
- Steht dort nur „Werke von Komponist A, B, C" (ohne Einzelwerke, z. B. Lied-/Arienabende),
  wird dieser Text als `description` gesetzt – die Event-Seite zeigt ihn über den
  „Werke von …"-Fallback an.
- Bei Education-/Familien-/Open-Air-Formaten (Klasse!Klassik, IGA, Neujahr, Sommerkonzert
  u. Ä.) ist quellseitig keine Werkangabe vorhanden → `program` bleibt leer.

## Spielstätten

Alle Spielstätten liegen in Duisburg. Neu angelegt: `mercatorhalle-duisburg` (Philharmonie
Mercatorhalle, Hauptspielstätte), `kueppersmuehle-duisburg`, `lehmbruck-museum-duisburg`,
`landschaftspark-duisburg-nord`, `salvatorkirche-duisburg`, `marienkirche-duisburg`,
`kulturkirche-liebfrauen-duisburg-mitte`, `st-maximilian-in-duisburg-ruhrort`,
`naturwerkstatt-wambachsee-duisburg`. Das bestehende `theater-duisburg` (Opernhaus) wird
wiederverwendet. Einen Duisburg-Fallback gibt es bewusst nicht – nicht zuordenbare
(auswärtige) Orte führen zum Ausschluss des Konzerts.

## Idempotenz

Vor dem Schreiben werden alle Events mit Quell-Host `duisburger-philharmoniker.de` und
Ensemble `duisburger-philharmoniker` entfernt und neu angelegt; Stammdaten werden nur ergänzt,
wenn ID/Schlüssel fehlen.

## Offene Punkte / Grenzen

- Programm-Abdeckung 40/67: Education-/Familien-/Open-Air-Formate haben keine Werkangabe.
- Auswärts-/Gastspiele der Philharmoniker (Orte außerhalb Duisburgs) sind nicht enthalten.
- `genre` ist heuristisch; `yearComposed`/`life` sind `null` – spätere Anreicherung möglich.
- Besetzungs-/Programmerkennung ist heuristisch; Stichproben-Abgleich empfohlen.
