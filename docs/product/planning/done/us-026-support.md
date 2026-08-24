# User Story 026 - Support und Projekt

## User Story

**Als** Betreiber von Klangland,  
**möchte ich** eine eigene Seite mit Projektvorstellung und Unterstützungsoption bereitstellen,  
**damit** Besucher:innen den Hintergrund des Projekts verstehen und es bei Interesse freiwillig finanziell unterstützen können.

## Kontext / Problem

Aktuell fehlt eine dedizierte Seite, die

- das Projekt kurz erklärt,
- den Entstehungskontext im OK Lab Köln sichtbar macht,
- ein Portrait der Projektverantwortung zeigt,
- und einen klaren Unterstützungsaufruf (PayPal) enthält.

Zusätzlich ist noch offen, wie die Seite benannt werden soll.  
Die Seite soll über die Hauptnavigation erreichbar sein, dort als letzter Menüpunkt erscheinen und optisch von den übrigen Punkten getrennt werden.

## Gewählte Lösung

Es wird eine neue statische Inhaltsseite im bestehenden Routing-/Seitenmuster angelegt.

Inhalte der Seite:

1. **Einleitung / Projektkontext** mit klarem Hinweis direkt am Anfang, dass Klangland im Rahmen des **OK Lab Köln** entstanden ist (https://codefor.de/koeln/).
2. **Kurze Projektzusammenfassung** inkl. Projektziel.  
   > Klangland zeigt dir, welche Konzerte in Nordrhein-Westfalen stattfinden – an einem Ort, aktuell und kostenlos. Das Projekt sammelt den Spielplan der professionellen Musikszene der Region: Sinfoniekonzerte, Oper, Kammermusik und perspektivisch auch Jazz. Im Kalender findest du Termine nach Datum, Ort und Ensemble. Du kannst Spielstätten auf einer Karte entdecken, durch Komponist:innen und Werke der Saison stöbern und mit der Suche schnell finden, was dich interessiert. Konzerte, die dich reizen, kannst du als Favoriten merken. Klangland läuft im Browser – am Rechner genauso wie auf dem Smartphone. Schau rein und finde dein nächstes Konzert.
3. **Portraitbild** des Betreibers, **rechteckig** dargestellt (Quelle: https://github.com/weberius/fotopfade/blob/main/images/koeln-muelheim/wolfram.jpg).
4. **Unterstützungsbereich** mit PayPal-Link auf Basis der vorhandenen Vorlage  
   (https://github.com/weberius/fotopfade/blob/main/locales/koeln-muelheim/de/bymecoffeeModalLi.md).
5. **Attribution am Seitenende** entfällt – wird durch separate Attributions-Seite gelöst.

Navigation:

- Neuer Eintrag in der Hauptnavigation als **letzter Menüpunkt**.
- Der Menüpunkt wird visuell durch einen **Trennstrich** von den übrigen Menüpunkten abgesetzt.

## Akzeptanzkriterien

1. Es existiert eine neue, per Route `/projekt` direkt aufrufbare Projekt-Seite.
2. Die Seite beginnt mit dem expliziten Hinweis auf den Entstehungskontext im OK Lab Köln (inkl. Link).
3. Die Seite enthält eine kurze, verständliche Zusammenfassung von Projekt und Projektziel.
4. Das definierte Portraitbild wird auf der Seite **rechteckig** angezeigt.
5. Die Seite enthält einen gut sichtbaren PayPal-Unterstützungslink.
6. In der Hauptnavigation ist der neue Menüpunkt "Projekt" der letzte Eintrag.
7. Der neue Menüpunkt ist durch einen Trennstrich von den übrigen Menüpunkten abgehoben.
8. Der neue Menüpunkt ist per Tastatur erreichbar und der Fokuszustand ist sichtbar.

## Out of Scope

- Technische Änderungen an Datenquellen (Open Opus, Wikipedia/Wikimedia).
- Einführung weiterer Bezahlanbieter neben PayPal.
- Mehrsprachige Versionen der Seite.

## Design-Entscheidungen ✅

1. **Seitenname und Routenpfad:** `Projekt` (Route: `/projekt`)
2. **Navigationstext:** `Projekt`
3. **PayPal-Ziel:** PayPal Donate-URL wie in der Vorlage-Vorlage (https://www.paypal.com/donate/?hosted_button_id=...)
4. **Portraitdarstellung:** Rechteckig
5. **Attributionslinks:** Entfällt – Attributions-Seite existiert bereits separat