# User Story 021 - Favoriten für Events (markieren, filtern, teilen)

## User Story

**Als** Besucher:in von Klangland,
**möchte ich** einzelne Konzerte als Favoriten markieren, die Anzeige auf meine Favoriten
einschränken und meine Auswahl per Link teilen können,
**damit** ich mir interessante Termine merke, schnell wiederfinde und mit anderen teilen bzw.
als Lesezeichen ablegen kann.

## Kontext / Problem

Klangland zeigt Events im Kalender ([calendar.html](../../../../web/src/app/pages/calendar/calendar.html))
und auf der Event-Detailseite ([event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html)),
bietet aber keine Möglichkeit, einzelne Konzerte hervorzuheben oder eine persönliche Auswahl
zusammenzustellen. Wer mehrere interessante Termine sichten will, verliert bei wachsendem
Datenbestand schnell den Überblick und kann seine Auswahl auch nicht weitergeben.

Mit [US-020](../done/us-020-filter.md) existiert bereits ein globales Filter-Popover
([filter-button](../../../../web/src/app/shared/filter-button/), [FilterService](../../../../web/src/app/core/filter.service.ts))
für Ort und Musikprofil. Ein Favoriten-Mechanismus lässt sich hier natürlich einhängen.

Klangland ist eine **statische App ohne Backend**; eine dauerhafte, nutzerbezogene Speicherung
ist nicht vorgesehen. Diese Story baut auf US-020 auf und ergänzt die dort begonnene
Kalender-Story US-012 (Kalender-Export) um die Merk-/Teilen-Funktion.

**Betroffen** sind die Event-Detailseite, die Event-Übersicht (Kalender), das Filter-Popover und
der geteilte Auswahl-Zustand. **Nicht betroffen** sind die Ensemble- und Spielstätten-Listen in
ihrer Filterlogik (Favoriten sind eventspezifisch) sowie die bestehende Ort-/Profil-Filterung.

## Gewählte Lösung

**Favoriten als flüchtige, eventbezogene Markierung mit Filter im vorhandenen Popover und
Teilen per Link auf Abruf.**

- **Markieren:** In der Event-Detailansicht wird ein Favoriten-Symbol (Stern) ergänzt, das den
  aktuellen Event als Favorit an- bzw. abwählt. Favoriten gelten ausschließlich für Events.
- **Anzeigen:** In der Event-Übersicht (Kalender-Kacheln/Agenda) werden favorisierte Events mit
  einem Stern in der rechten oberen Ecke markiert.
- **Filtern:** Im US-020-Filter-Popover gibt es eine Umschaltung „Nur Favoriten". Sie schränkt
  die Event-Anzeige (Kalender) auf Favoriten ein und wird mit Ort/Profil **UND**-kombiniert
  (Städte ODER-verknüpft, Profile ODER-verknüpft, Kategorien untereinander UND). Beispiel:
  „Nur Favoriten" + Köln/Düsseldorf + Klassik/Oper → favorisierte Konzerte mit Klassik oder Oper
  in Köln oder Düsseldorf.
- **Zurücksetzen:** „Alle zurücksetzen" im Popover entfernt neben den Ort-/Profil-Filtern auch
  den Favoriten-Filter **und** die gesetzten Favoriten-Markierungen.
- **Teilen:** Eine Aktion erzeugt auf Abruf einen Link, dessen Query-Parameter die favorisierten
  Events kodieren. Über diesen Link lässt sich die Auswahl teilen oder als Lesezeichen ablegen;
  beim Öffnen des Links werden die Favoriten beim Laden wiederhergestellt.

**Persistenz:** Favoriten leben nur im Speicher (kein `localStorage`/`sessionStorage`). Der
Aufruf/Reload der Basis-Adresse ohne Favoriten-Parameter zeigt keine Favoriten; einzig ein
geteilter Link mit Parametern stellt sie her.

Bewusst verworfen: dauerhafte Speicherung pro Gerät und das Kodieren der Ort-/Profil-Filter in
der URL – hier wird nur die Favoriten-Auswahl geteilt.

## Akzeptanzkriterien

1. **Markieren in Detailansicht:** Auf der Event-Detailseite gibt es ein Favoriten-Symbol
   (Stern), das den Event als Favorit an- und wieder abwählt und seinen Zustand sichtbar anzeigt.
2. **Nur Events:** Favoriten können ausschließlich auf Events angewendet werden (nicht auf
   Ensembles oder Spielstätten).
3. **Markierung in Übersicht:** Favorisierte Events sind in der Event-Übersicht (Kalender-Kachel
   bzw. Agenda) mit einem Stern in der rechten oberen Ecke gekennzeichnet.
4. **Flüchtiger Zustand:** Der Favoriten-Zustand wird im Speicher gehalten; es findet keine
   Persistenz über `localStorage`/`sessionStorage` statt.
5. **Favoriten-Filter:** Im Filter-Popover (US-020) lässt sich „Nur Favoriten" ein- und
   ausschalten.
6. **Kombinierte Filterung:** Bei aktivem „Nur Favoriten" zeigt der Kalender nur favorisierte
   Events; ist zusätzlich Ort und/oder Profil gewählt, wird UND-kombiniert (innerhalb Ort bzw.
   Profil jeweils ODER).
7. **Geltungsbereich:** Der Favoriten-Filter wirkt auf die Event-Anzeige (Kalender); die
   Ensemble- und Spielstätten-Liste bleiben von ihm unberührt.
8. **Zurücksetzen:** „Alle zurücksetzen" im Popover entfernt die Ort-/Profil-Filter, den
   Favoriten-Filter und die gesetzten Favoriten-Markierungen.
9. **Teilen-Link:** Eine Aktion erzeugt auf Abruf einen Link, dessen Query-Parameter die
   favorisierten Events kodieren (teil- und bookmarkbar).
10. **Wiederherstellen:** Das Öffnen eines geteilten Links stellt die enthaltenen Favoriten beim
    Laden der App wieder her.
11. **Kein Rest ohne Parameter:** Aufruf/Reload der Adresse ohne Favoriten-Parameter zeigt keine
    Favoriten.
12. **Standardzustand:** Ohne Zutun sind keine Favoriten gesetzt und der Favoriten-Filter ist
    aus.
13. **Barrierefreiheit:** Stern-Toggle und Favoriten-Umschaltung sind echte, per Tastatur
    bedienbare Bedienelemente und kommunizieren ihren Zustand (z. B. `aria-pressed`) an assistive
    Technologien.
14. **Unveränderte Bereiche:** Die bestehende Ort-/Profil-Filterlogik und die übrigen Inhalte der
    Event-Detailseite bleiben unverändert.

## Out of Scope

- Dauerhafte, gerätegebundene Speicherung der Favoriten (`localStorage`/`sessionStorage`,
  Nutzerkonten, Backend) – Wiederherstellung nur über den geteilten Link.
- Favoriten für Ensembles oder Spielstätten.
- Kodierung der Ort-/Profil-Filter in der URL (nur die Favoriten-Auswahl wird geteilt).
- Kalender-Export einzelner Termine (eigene Story US-012).
- Benachrichtigungen/Erinnerungen zu Favoriten.

<!--
Umsetzungs-Tasks in separater Datei US-021-tasks.md im selben Verzeichnis pflegen.
-->
