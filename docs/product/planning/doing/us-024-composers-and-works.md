# User Story 024 - Komponist:innen-Seiten und Werk-Anreicherung

## User Story

**Als** Besucher:in von Klangland,
**möchte ich** die gespielten Komponist:innen auf einer eigenen Seite alphabetisch durchstöbern und je Komponist:in eine Detailseite mit Lebensdaten, Einordnung, Portrait, gespielten Werken und zugehörigen Veranstaltungen öffnen können,
**damit** ich das Repertoire der Saison auch von der Komponist:in her erschließen und fundierte Hintergründe zu Person und Werk finden kann.

## Kontext / Problem

Mit [US-017](../done/US-017-open-opus.md) wurden Komponist:innen- und Werkdaten aus Open Opus (strukturierte Metadaten) und Wikipedia (kuratierte Kurzfassungen) angereichert und in [composers.json](../../../../data/composers.json) sowie [works.json](../../../../data/works.json) gepflegt. Das [`Composer`-Modell](../../../../web/src/app/models/models.ts#L131-L141) kennt seither `openOpusId`, `epoch` und `wikipedia`, das [`Work`-Modell](../../../../web/src/app/models/models.ts#L158-L176) zusätzlich `popular`/`recommended`. Diese Daten liegen jedoch **nur in den JSON-Dateien** und werden in der UI noch nicht sichtbar.

Die Werke sind seit [US-018](../done/US-018-works.md) bereits als eigene Seiten erschlossen: eine Übersicht unter `/works` und eine Detailseite unter `/works/:id` ([app.routes.ts:40-49](../../../../web/src/app/app.routes.ts#L40-L49), [work-detail](../../../../web/src/app/pages/work-detail/)). Dort wird der Komponist bislang nur als **Text** angezeigt – bewusst als offener Punkt für diese Story vermerkt ([US-018, Gewählte Lösung](../done/US-018-works.md#L27-L30)). Für **Komponist:innen** fehlt bisher jede eigene Seite; die Hauptnavigation führt zu Kalender, Ensembles, Spielstätten, Werke und Karte ([app.html:71-75](../../../../web/src/app/app.html#L71-L75)).

Der [`DataService`](../../../../web/src/app/core/data.service.ts) bietet bereits `composer(id)`, `work(id)`, `eventsForWork(id)` sowie den kombinierten Ort-/Profil-Filter aus [US-020](../done/us-020-filter.md) (`eventsForFilter`, `worksForFilter`, [data.service.ts:368-383](../../../../web/src/app/core/data.service.ts#L368-L383)). Eine komponistenbezogene Ableitung (gespielte Werke, Veranstaltungen) fehlt noch.

Hinzu kommt die **Bildfrage**: Portraits wurden in US-017 zunächst ausgeklammert, solange die Lizenz ungeklärt ist ([US-017, Out of Scope](../done/US-017-open-opus.md#L68)). Für ansprechende Komponisten-Kacheln und -Detailseiten werden Bilder benötigt. Als Quelle dienen Wikipedia/Wikimedia Commons, deren Lizenzfrage in der Regel geklärt ist; die Bilder werden lokal persistiert und mit sichtbarem Quellenverweis attribuiert. Damit ist der Vorbehalt aus US-017 für diese Story aufgelöst.

Als fachliches Vorbild dienen die **Venue-Seiten** (Übersicht als Kachel-Grid + Detail mit Event-Liste) und die bereits umgesetzte **Werke-Seite** (US-018) sowie die Wikipedia-Attribution auf der Ensemble-Detailseite ([ensemble-detail.html:57](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html#L57)).

## Gewählte Lösung

### 1. Komponist:innen-Seiten (`/composers`, `/composers/:id`)

Es werden zwei neue Seiten analog zu den Venue-/Werke-Seiten angelegt und ein Navigationspunkt **„Komponist:innen"** in die Hauptnavigation aufgenommen.

**Übersicht** (`/composers`): Kachel-Grid im vorhandenen `.card-grid`-Stil, **alphabetisch nach Komponist:innen-Name** sortiert (`localeCompare('de')`). Angezeigt werden nur Komponist:innen, die über den geltenden **Ort-/Profil-Filter (US-020)** in der geladenen Saison tatsächlich mit mindestens einem Werk programmiert sind (analog zu `worksForFilter`). Jede Kachel zeigt Name, Lebensdaten, – falls vorhanden – das Portrait sowie die Liste der in der Saison gespielten Werke der Komponist:in. Ein Klick öffnet die Detailseite.

**Detail** (`/composers/:id`): zeigt Name, Lebensdaten, Epoche und die kuratierte Wikipedia-Kurzfassung samt Quellenverweis (analog Ensemble-Detail), sofern gepflegt, sowie das Portrait mit Bild-Attribution. Darunter eine **Liste der gespielten Werke** (jeder Eintrag verlinkt auf `/works/:id`) und darunter eine chronologische **Liste der Veranstaltungen**, in deren Programm Musik dieser Komponist:in vorkommt (wiederverwendbare [`EventList`](../../../../web/src/app/shared/event-list.ts)). Eine unbekannte ID führt zur bestehenden „nicht gefunden"-Behandlung.

Der `DataService` erhält dazu abgeleitete Methoden (ohne neuen Cache), insbesondere `composersForFilter(...)`, `worksForComposer(composerId, ...)` und `eventsForComposer(composerId, ...)`, konsistent zu den vorhandenen `*ForFilter`-/`*ForWork`-Methoden.

### 2. Werk-Detailseite erweitern

Die bestehende Werk-Detailseite (`/works/:id`) wird ergänzt:
* Der **Komponistenname wird auf `/composers/:id` verlinkt** (löst den in US-018 offen gelassenen Punkt).
* Die in US-017 gepflegte **Open-Opus-/Wikipedia-Anreicherung** wird sichtbar gemacht: Epoche der Komponist:in (Kontext), Werk-Wikipedia-Kurzfassung samt Quellenverweis sowie ggf. die Kennzeichen `popular`/`recommended` – jeweils nur, wenn gepflegt.

Die Route bleibt `/works/:id`; die vorhandenen, titelnahen Slug-IDs (z. B. `works.json`) werden weiterverwendet (der Wunsch „URL über Titel bzw. workId" ist damit bereits erfüllt). Die Werke-Übersicht (`/works`) bleibt inhaltlich unverändert.

### 3. Bilder aus Wikipedia/Wikimedia Commons (Download + Attribution)

* Ein **Python-Tool** (analog zum Open-Opus-Importer, keine Laufzeitabhängigkeit) recherchiert zu den programmierten Komponist:innen Portraits über Wikipedia/Wikimedia Commons, **lädt sie herunter** und legt sie als **committete Projekt-Assets** ab (die App bindet lokale Dateien ein, referenziert **keine** Fremd-URLs zur Laufzeit).
* Bilder werden – **sofern vorhanden** – aus Wikipedia/Wikimedia Commons bezogen; die Lizenzfrage ist bei dieser Quelle in der Regel geklärt. Zu jedem Bild wird die **Quelle** (Quell-URL) mitgepflegt, auf die die Attribution verweist.
* Das `Composer`-Modell und `composers.json` erhalten dafür ein optionales **Portrait-Feld** samt Quellenverweis. Komponist:innen ohne Portrait bleiben valide; Kachel und Detailseite funktionieren ohne Bild (sinnvoller Platzhalter/Weglassen).
* Bei jeder Bildanzeige wird die **Attribution sichtbar** dargestellt und verweist auf die **Quelle** (Wikipedia/Wikimedia Commons), analog zur Wikipedia-Attribution auf der Ensemble-Detailseite und zur Karten-Attribution.
* **Schonender Abruf:** Recherche/Download begrenzen Netzwerkzugriffe auf **höchstens einen Request pro Sekunde** und cachen wo möglich lokal (konsistent zu [US-017, AK 11](../done/US-017-open-opus.md#L61)).

Bewusst akzeptierte Kompromisse:
* Sortierung nach „Name" nutzt das vorhandene `Composer.name` (kein separater Nachname; echte Nachnamen-Sortierung ist nicht Teil dieser Story) – konsistent zu US-018.
* Portraits/Attributionen sind redaktionelle Momentaufnahmen und aktualisieren sich nicht automatisch.
* Es wird kein neuer `DataService`-Zustand/Cache eingeführt, wenn eine einfache abgeleitete Berechnung genügt (analog zu `eventsForVenue`/`worksForFilter`).

## Akzeptanzkriterien

1. **Route Komponist:innen-Übersicht:** Unter `/composers` ist eine Übersicht erreichbar; der Titel folgt dem Muster der übrigen Seiten (`… · Klangland`).
2. **Route Komponist:innen-Detail:** Unter `/composers/:id` ist die Detailseite erreichbar; eine unbekannte ID führt zu einer sinnvollen „nicht gefunden"-Behandlung (analog zu bestehenden Detailseiten).
3. **Navigation:** Die Hauptnavigation enthält einen Punkt „Komponist:innen", der auf `/composers` verweist und den Aktiv-Zustand korrekt anzeigt (`routerLinkActive`), konsistent zu den übrigen Navigationspunkten.
4. **Umfang/Filter:** In der Übersicht erscheinen ausschließlich Komponist:innen, die – unter dem geltenden Ort-/Profil-Filter (US-020) – in mindestens einem Event-Programm der geladenen Saison vorkommen; jede Komponist:in erscheint genau einmal. Bei leerer Filterauswahl gelten alle programmierten Komponist:innen (analog `worksForFilter`).
5. **Sortierung:** Die Kacheln sind alphabetisch nach Komponist:innen-Name sortiert (`localeCompare('de')`).
6. **Kachel-Inhalt:** Eine Kachel zeigt Name und Lebensdaten, das Portrait (falls vorhanden, sonst sauberes Weglassen/Platzhalter) sowie die Liste der in der Saison gespielten Werke der Komponist:in. Die Kachel ist als Ganzes anklickbar und verlinkt auf `/composers/:id`.
7. **Detail-Informationen:** Die Detailseite zeigt Name und Lebensdaten sowie – jeweils nur, wenn gepflegt – Epoche und die Wikipedia-Kurzfassung mit sichtbarem Quellenverweis (analog Ensemble-Detail). Nicht gepflegte Felder erzeugen keine leeren Zeilen.
8. **Gespielte Werke:** Die Detailseite listet die in der Saison gespielten Werke der Komponist:in; jeder Eintrag verlinkt auf die jeweilige Werk-Detailseite (`/works/:id`).
9. **Veranstaltungsliste:** Die Detailseite enthält – unterhalb der Details – eine chronologisch sortierte Liste der Veranstaltungen, in deren Programm Musik der Komponist:in vorkommt; jeder Eintrag verlinkt auf die Event-Detailseite (wiederverwendete `EventList`).
10. **Werk-Detail – Komponisten-Verlinkung:** Auf `/works/:id` wird der Komponistenname auf `/composers/:id` verlinkt (per Tastatur erreichbar).
11. **Werk-Detail – Anreicherung:** Auf `/works/:id` werden die in US-017 gepflegten Anreicherungen sichtbar gemacht (Epoche der Komponist:in, Werk-Wikipedia-Kurzfassung mit Quellenverweis, ggf. `popular`/`recommended`), jeweils nur wenn gepflegt; nicht gepflegte Angaben werden ausgelassen.
12. **Bild-Datenmodell:** `Composer` und `composers.json` unterstützen ein optionales Portrait-Feld inklusive Quellenverweis (Quell-URL zu Wikipedia/Wikimedia Commons). Datensätze ohne Portrait bleiben valide.
13. **Bild-Download-Tool:** Ein Python-Tool lädt – sofern vorhanden – Portraits aus Wikipedia/Wikimedia Commons herunter und legt sie als committete Projekt-Assets ab; die Webanwendung bindet lokale Dateien ein und ruft zur Laufzeit **keine** Fremd-URLs für Bilder ab.
14. **Attribution Bilder:** Bilder werden aus Wikipedia/Wikimedia Commons bezogen (Lizenzfrage dort in der Regel geklärt); bei jeder Bildanzeige wird die Attribution sichtbar dargestellt und verweist auf die Quelle.
15. **Schonender Abruf / Rate-Limiting:** Recherche- und Download-Skripte begrenzen Netzwerkzugriffe auf **maximal einen Request pro Sekunde** und cachen wo möglich lokal (konsistent zu US-017).
16. **Konsistenz/Barrierefreiheit:** Layout, Kartenstil, Zurück-Link und Überschriftenstruktur orientieren sich an den Venue-/Werke-Seiten; die Übersicht hat eine Seitenüberschrift (`app-page-header`); Kacheln, Werk- und Event-Links sind per Tastatur erreichbar; Portraits haben aussagekräftige `alt`-Texte.
17. **Versionierung:** Neue Bild-Assets sowie Modell-/Datenänderungen sind über Git nachvollziehbar versioniert.
18. **Unveränderte Bereiche:** Die Werke-Übersicht (`/works`) sowie alle übrigen bestehenden Seiten und Verhaltensweisen bleiben unverändert.

## Out of Scope

- Filter-/Suchfunktion speziell für Komponist:innen (über den bestehenden globalen Ort-/Profil-Filter hinaus).
- Anzeige von Komponist:innen, die in keinem Event der Saison programmiert sind.
- Werk-Portraits/-Bilder (nur Komponisten-Portraits sind Gegenstand dieser Story).
- Live-Abruf von Open Opus, Wikipedia oder Wikimedia Commons zur Laufzeit der Webanwendung.
- Automatische Aktualisierung von Kurzfassungen, Metadaten oder Bildern.
- Änderungen an der Sortierlogik hin zu echter Nachnamen-Sortierung.
- Mehrsprachigkeit (nur Deutsch).

<!--
Umsetzungs-Tasks:
In separater Datei us-024-tasks.md im selben Verzeichnis pflegen.
Struktur dort: nummerierte Tasks (je betroffene Datei/Verantwortlichkeit), pro Task konkrete Schritte
mit Bezug auf die Akzeptanzkriterien, ein Abschnitt "Manuelle Verifikation" und eine "Definition of Done".
-->
