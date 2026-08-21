# User Story 014 - Wikipedia-Kurzfassung und Link auf der Ensemble-Seite

## User Story

**Als** Besucher:in einer Ensemble-Detailseite,
**möchte ich** eine kurze, verständliche Zusammenfassung zum Ensemble aus der Wikipedia samt Link zum vollständigen Artikel sehen,
**damit** ich mich schnell einlesen und bei Bedarf vertiefend weiterlesen kann, ohne selbst danach suchen zu müssen.

## Kontext / Problem

Die Ensemble-Detailseite zeigt heute nur die im Projekt gepflegten Basisinformationen: Kurzbeschreibung (`description`), Profil-Tags, Fakten (Chefdirigent:in, Sitz, Stammsaal, Träger) sowie einen Link auf die offizielle Website ([ensemble-detail.html:13-51](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html#L13-L51)). Eine allgemein verständliche, redaktionell aufbereitete Einordnung des Ensembles fehlt, und Nutzer:innen müssen für weiterführende Informationen selbst recherchieren.

Das Datenmodell [`Ensemble`](../../../../web/src/app/models/models.ts#L89-L104) kennt bisher kein Feld für Wikipedia-Informationen. Die Daten werden in [ensembles.json](../../../../data/ensembles.json) gepflegt.

Betroffen ist ausschließlich die **Ensemble-Detailseite**. Die Ensemble-Übersicht ([ensemble-list](../../../../web/src/app/pages/ensemble-list/)) sowie andere Detailseiten (Venues, Personen, Kalender) bleiben unverändert.

## Gewählte Lösung

Die Wikipedia-Informationen werden **kuratiert in den Projektdaten** gepflegt, nicht zur Laufzeit von der Wikipedia geladen. Dazu erhält jedes Ensemble in [ensembles.json](../../../../data/ensembles.json) optionale Felder für die Wikipedia-URL und eine **eigene, sinngemäße Zusammenfassung von ca. 60 Wörtern** (kein wörtlicher Auszug). Diese Zusammenfassung wird im Rahmen dieser Story pro Ensemble recherchiert und formuliert (Internet-Recherche nach dem geeigneten Wikipedia-Artikel ist Teil des Tickets).

Auf der Detailseite wird ein Wikipedia-Abschnitt dargestellt, der die Kurzfassung, eine **Quellen-/Attributierung** (Verweis auf den Wikipedia-Artikel als Grundlage) und einen **Link zum vollständigen Artikel** enthält. Der Abschnitt erscheint nur, wenn für das Ensemble Wikipedia-Daten gepflegt sind; andernfalls bleibt die Seite unverändert.

Bewusst akzeptierter Kompromiss: Die Zusammenfassung ist eine redaktionell erstellte Momentaufnahme und aktualisiert sich nicht automatisch, wenn sich der Wikipedia-Artikel ändert.

## Akzeptanzkriterien

1. **Datenmodell:** Das `Ensemble`-Modell und die Daten in [ensembles.json](../../../../data/ensembles.json) unterstützen optionale Wikipedia-Angaben (mindestens: URL zum Artikel und Kurzfassung). Ensembles ohne diese Angaben bleiben valide.
2. **Kurzfassung:** Ist eine Wikipedia-Kurzfassung gepflegt, wird sie im Wikipedia-Abschnitt der Detailseite als eigenständig formulierter Text von ca. 60 Wörtern angezeigt.
3. **Attributierung:** Unterhalb der Kurzfassung wird die Quelle attribuiert (erkennbarer Hinweis, dass die Zusammenfassung auf dem Wikipedia-Artikel basiert, inkl. Verweis auf Wikipedia).
4. **Link zum Artikel:** Ein Link ermöglicht das Öffnen des vollständigen Wikipedia-Artikels; er öffnet in einem neuen Tab (`target="_blank"`, `rel="noopener"`) analog zum bestehenden Website-Link.
5. **Kein Artikel vorhanden:** Ist für ein Ensemble keine Wikipedia-Angabe gepflegt, wird der Wikipedia-Abschnitt vollständig ausgeblendet; die übrige Seite bleibt unverändert.
6. **Recherche/Datenpflege:** Für die Ensembles in [ensembles.json](../../../../data/ensembles.json) werden die passenden Wikipedia-Artikel recherchiert und – wo ein geeigneter Artikel existiert – URL und Kurzfassung gepflegt.
7. **Bestehende Inhalte:** Die vorhandenen Bereiche der Detailseite (Beschreibung, Profil-Tags, Fakten, Website-Link, Veranstaltungen) bleiben in Darstellung und Verhalten unverändert.
8. **Barrierefreiheit:** Der Wikipedia-Abschnitt ist semantisch klar ausgezeichnet (Überschrift), und der Artikel-Link ist per Tastatur erreichbar und aussagekräftig benannt.

## Out of Scope

- Live-Abruf der Wikipedia-Inhalte über die Wikipedia-API zur Laufzeit (bewusst zugunsten kuratierter Daten nicht gewählt).
- Automatische Generierung oder Aktualisierung der Kurzfassung.
- Anzeige von Wikipedia-Informationen auf anderen Seiten (Ensemble-Übersicht, Venues, Personen).
- Einbindung von Bildern/Medien aus der Wikipedia.
- Mehrsprachigkeit der Kurzfassung (nur Deutsch).

<!--
Umsetzungs-Tasks:
In separater Datei US-014-tasks.md im selben Verzeichnis pflegen.
Struktur dort: nummerierte Tasks (je betroffene Datei/Verantwortlichkeit), pro Task konkrete Schritte
mit Bezug auf die Akzeptanzkriterien, ein Abschnitt "Manuelle Verifikation" und eine "Definition of Done".
-->
