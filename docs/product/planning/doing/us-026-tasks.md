# US-026 Tasks - Projekt-Seite

## Task-Übersicht

### 1. Seite im bestehenden Pattern erstellen
**ID:** us026-page-structure  
**Status:** Pending  
**Abhängigkeiten:** Keine  
**Beschreibung:**  
Neue statische Inhaltsseite nach bestehendem Routing-/Seitenmuster anlegen:
- Route: `/projekt`
- Seitentitel: "Projekt"
- Grundstruktur mit allen 4 Inhaltsbereichen vorbereiten:
  1. Einleitung/OK Lab Kontext
  2. Projektzusammenfassung
  3. Portraitbild (rechteckig)
  4. PayPal-Unterstützungsbereich
- CSS/Styling für die Seite vorbereiten

---

### 2. OK Lab Köln Kontext implementieren
**ID:** us026-oklab-context  
**Status:** Pending  
**Abhängigkeiten:** us026-page-structure  
**Beschreibung:**  
Einleitungsbereich mit explizitem Hinweis auf OK Lab Köln umsetzen:
- Klarer Text, dass Klangland im Rahmen des OK Lab entstanden ist
- Link zu https://codefor.de/koeln/ einbinden
- Prominent am Anfang der Seite platzieren (AC-2)

---

### 3. Projektzusammenfassung einbinden
**ID:** us026-project-summary  
**Status:** Pending  
**Abhängigkeiten:** us026-page-structure  
**Beschreibung:**  
Die bereitgestellte Projektzusammenfassung einbinden:
> Klangland zeigt dir, welche Konzerte in Nordrhein-Westfalen stattfinden – an einem Ort, aktuell und kostenlos. Das Projekt sammelt den Spielplan der professionellen Musikszene der Region: Sinfoniekonzerte, Oper, Kammermusik und perspektivisch auch Jazz. Im Kalender findest du Termine nach Datum, Ort und Ensemble. Du kannst Spielstätten auf einer Karte entdecken, durch Komponist:innen und Werke der Saison stöbern und mit der Suche schnell finden, was dich interessiert. Konzerte, die dich reizen, kannst du als Favoriten merken. Klangland läuft im Browser – am Rechner genauso wie auf dem Smartphone. Schau rein und finde dein nächstes Konzert.

Anforderungen:
- Text sollte Projektziel und Funktionen verständlich darstellen (AC-3)

---

### 4. Portraitbild einbinden
**ID:** us026-portrait-integration  
**Status:** Pending  
**Abhängigkeiten:** us026-page-structure  
**Beschreibung:**  
Portraitbild des Betreibers einbinden und **rechteckig** darstellen:
- Bildquelle: https://github.com/weberius/fotopfade/blob/main/images/koeln-muelheim/wolfram.jpg
- Darstellung: **Rechteckig** (nicht rund, nicht original)
- Angemessene Auflösung und Performance optimieren (responsive Bilder)
- Bild sollte auf der Seite sichtbar sein (AC-4)

---

### 5. PayPal-Unterstützungsbereich implementieren
**ID:** us026-paypal-support  
**Status:** Pending  
**Abhängigkeiten:** us026-page-structure  
**Beschreibung:**  
Unterstützungsbereich mit PayPal-Link umsetzen:
- Basierend auf Vorlage: https://github.com/weberius/fotopfade/blob/main/locales/koeln-muelheim/de/bymecoffeeModalLi.md
- PayPal-Donate-URL wie in der Vorlage verwenden
- Bereich sollte gut sichtbar und prominent platziert sein
- Funktionsfähiger PayPal-Link (AC-5)

---

### 6. Navigation aktualisieren
**ID:** us026-navigation-update  
**Status:** Pending  
**Abhängigkeiten:** us026-page-structure  
**Beschreibung:**  
Hauptnavigation mit neuem Menüpunkt aktualisieren:
- Neuen Menüeintrag "Projekt" hinzufügen
- Als **letzter Menüpunkt** positionieren (AC-6)
- **Visuellen Trennstrich** vor dem neuen Menüpunkt implementieren (CSS/Styling) (AC-7)
- Link zur Route `/projekt` setzen

---

### 7. Accessibility prüfen und implementieren
**ID:** us026-accessibility  
**Status:** Pending  
**Abhängigkeiten:** us026-oklab-context, us026-project-summary, us026-portrait-integration, us026-paypal-support, us026-navigation-update  
**Beschreibung:**  
Keyboard-Navigation und Fokus-Styling sicherstellen:
- Neuer Menüpunkt "Projekt" per Tastatur erreichbar (AC-8)
- Sichtbarer Fokuszustand auf dem Menüpunkt vorhanden
- Alle Links auf der Seite keyboard-accessible
- Tab-Reihenfolge logisch
- Kontrast und Lesbarkeit prüfen

---

### 8. Review und Testen
**ID:** us026-review-testing  
**Status:** Pending  
**Abhängigkeiten:** us026-accessibility  
**Beschreibung:**  
Vollständiger Test gegen alle 8 Akzeptanzkriterien:
- **Visueller Review**: Layout, Styling, Responsive Design (Desktop & Mobile)
- **Funktionalitätscheck**: Alle Links funktionieren, Bilder laden, PayPal-Link funktioniert
- **Browser-Kompatibilität**: Chrome, Firefox, Safari, Edge
- **Accessibility-Test**: Keyboard-Navigation, Screen-Reader Kompatibilität
- **Performance**: Seitenladezeit, Bildoptimierung

Test-Checklist gegen AC:
- [ ] AC-1: Route `/projekt` ist aufrufbar
- [ ] AC-2: OK Lab Köln Hinweis mit Link vorhanden
- [ ] AC-3: Projektzusammenfassung verständlich
- [ ] AC-4: Portraitbild rechteckig dargestellt
- [ ] AC-5: PayPal-Link gut sichtbar und funktioniert
- [ ] AC-6: Neuer Menüpunkt "Projekt" ist letzter Eintrag
- [ ] AC-7: Trennstrich vor Menüpunkt sichtbar
- [ ] AC-8: Menüpunkt per Tastatur erreichbar mit sichtbarem Fokus

---

## Task-Abhängigkeiten (DAG)

```
us026-page-structure
  ├─ us026-oklab-context
  ├─ us026-project-summary
  ├─ us026-portrait-integration
  ├─ us026-paypal-support
  └─ us026-navigation-update
      └─ us026-accessibility
          └─ us026-review-testing
```

---

## Geschätzter Aufwand

| Task | Aufwand (h) |
|------|------------|
| Page Structure | 2-3 |
| OK Lab Context | 1 |
| Project Summary | 0.5 |
| Portrait Integration | 1-2 |
| PayPal Support | 1-2 |
| Navigation Update | 1-2 |
| Accessibility | 1-2 |
| Review & Testing | 2-3 |
| **Gesamt** | **9-17** |
