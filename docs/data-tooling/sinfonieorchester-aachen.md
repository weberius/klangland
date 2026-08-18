# Sinfonieorchester Aachen – Ingest 2026/27

Quelle: [Theater Aachen, Konzerte 26.27](https://www.theateraachen.de/de/seiten/konzerte-2627.html)
und die Detailseiten der einzelnen Sinfoniekonzerte
(`https://www.theateraachen.de/de/produktionen/<n>-sinfoniekonzert-3.html`).

Skript: [`ingest_aachen.py`](ingest_aachen.py)

## Umfang

Erfasst werden die **acht Sinfoniekonzerte** der Spielzeit 2026/27, jeweils mit **zwei
Aufführungen** (Samstag 19:00 Uhr / Sonntag 18:00 Uhr) im **Eurogress Aachen** →
insgesamt **16 Events**.

Bewusst **nicht** aufgenommen (kein Kernspielplan des Orchesters):

- **Kammerkonzerte 1–4** – Kammerensembles der Orchestermusiker:innen, nicht das
  Sinfonieorchester als Ganzes.
- **Sonderkonzerte** mit Fremdensembles: »Wunschkonzert« (Western Balkans Youth Orchestra),
  Wildes Holz »Block-Party«.

## Neu angelegte Stammdaten

- **Venue:** `eurogress-aachen` (Konzertsaal der Aachener Sinfoniekonzerte;
  Theater Aachen selbst existierte bereits als `theater-aachen`).
- **Komponist:innen (9):** John Rutter, Lili Boulanger, Alberto Ginastera,
  Xavier Montsalvatge, Manuel de Falla, Alexander Borodin, Jennifer Higdon,
  Giuseppe Verdi, Andrea Tarrodi.
- **Werke (21):** je Konzert die aufgeführten Werke; vorhandene Werke wurden über ihre IDs
  wiederverwendet (`kodaly-galantai-tancok`, `gershwin-amerikaner-in-paris`).
- **Personen (13):** Dirigent:innen Tomàs Grau, Felix Mildenberger, Riccardo Frizza
  (Levente Török existierte bereits als GMD) sowie die Solist:innen.

## Programmübersicht

| Nr. | Termine | Dirigent:in | Solist:innen | Hauptwerke |
| --- | --- | --- | --- | --- |
| 1 | 19./20.09.26 | Levente Török | – (mit Chören) | Elgar, Rutter, Boulanger, Ravel (Daphnis et Chloé) |
| 2 | 17./18.10.26 | Tomàs Grau | Clara Andrada (Fl.), Alexandra Urquiola (Mezzo) | Ginastera, Montsalvatge, de Falla |
| 3 | 14./15.11.26 | Levente Török | József Balog (Kl.) | Kodály, Dohnányi, Brahms 4 |
| 4 | 13./14.02.27 | Levente Török | Francesco de Angelis (Vl.) | Tschaikowsky VK, Borodin, Schostakowitsch 9 |
| 5 | 20./21.03.27 | Felix Mildenberger | Alexej Gerassimez (Schlagzeug) | Gershwin, Higdon, Dvořák 9 |
| 6 | 24./25.04.27 | Riccardo Frizza | Eloïse Bella Kohn (Kl.) | Beethoven (Leonore III, KK 5), Berlioz |
| 7 | 22./23.05.27 | Levente Török | Larisa Akbari, Mario Rojas, Max Bell (mit Chören) | Verdi: Messa da Requiem |
| 8 | 19./20.06.27 | Levente Török | Giulia Rimonda (Vl.) | Brahms VK, Tarrodi, Mozart 39 |

## Konventionen / Entscheidungen

- **Eine Aufführung = ein Event**; Event-IDs `event-YYYY-MM-DD-aachen-<n>-sinfoniekonzert`.
- **Ticket-Links:** je Aufführung die konkrete **Reservix**-URL (`ticketUrl`); die
  `source.url` verweist auf die Konzert-Detailseite.
- **Chöre** (Opernchor Aachen, Sinfonischer Chor Aachen) und die Choreinstudierung haben kein
  eigenes Feld im Modell und stehen daher im `description`-Freitext (Konzerte 1 und 7).
- `durationMinutes` bleibt `null` (nicht belegt); `genre` nutzt kontrollierte Werte.

## Idempotenz

Das Skript entfernt vor dem Schreiben alle Events mit Quell-Host `theateraachen.de` und dem
Ensemble `sinfonieorchester-aachen` und legt sie neu an; Stammdaten werden nur ergänzt, wenn
ihre ID noch fehlt. Ein erneuter Lauf ist damit gefahrlos wiederholbar.

## Offene Punkte

- Verdis »Messa da Requiem« (Konzert 7) wird üblicherweise mit vier Vokalsolist:innen
  (inkl. Mezzosopran/Alt) besetzt; die Quelle nannte zum Erfassungszeitpunkt nur Sopran,
  Tenor und Bass. Bei nächster Prüfung ggf. die vierte Solistin ergänzen.
