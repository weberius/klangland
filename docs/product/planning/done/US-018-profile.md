### User Story 018 - Ensemble-Typ, Professionalität und musikalisches Profil

**Als Betreiber von Klangland möchte ich Ensembles anhand ihres Typs, ihrer Professionalität, ihrer institutionellen Rollen und ihrer musikalischen Profile klassifizieren können, damit unterschiedliche professionelle Klangkörper – von Sinfonieorchestern über Opernorchester bis hin zu Ensembles für Alte Musik – einheitlich und flexibel dargestellt werden können.**

#### Akzeptanzkriterien

* Jedes Ensemble besitzt einen **grundlegenden `type`**, z. B.:

  * `orchestra`
  * `chamber_orchestra`
  * `ensemble`
  * `big_band`
  * `chorus`
  * `vocal_ensemble`

* Über `professional` wird angegeben, ob es sich um ein **professionelles Ensemble** handelt.

* Ein Ensemble kann mehrere **institutionelle bzw. musikalische Rollen** besitzen, z. B.:

  * `symphony_orchestra`
  * `opera_orchestra`
  * `theater_orchestra`
  * `state_orchestra`

* Ein Ensemble kann mehrere **musicalProfiles** besitzen, z. B.:

  * `classical`
  * `romantic`
  * `baroque`
  * `early_music`
  * `historically_informed_performance`
  * `contemporary`
  * `new_music`
  * `opera`
  * `musical`
  * `film_music`
  * `game_music`
  * `jazz`
  * `crossover`
  * `entertainment`
  * `choral`
  * `vocal`

* `type`, `roles` und `musicalProfiles` werden **getrennt modelliert**, da sie unterschiedliche Sachverhalte beschreiben:

  * `type` beschreibt, **was für ein Ensemble** es ist.
  * `roles` beschreibt, **welche institutionelle bzw. funktionale Aufgabe** es erfüllt.
  * `musicalProfiles` beschreibt, **welche musikalischen Schwerpunkte** es besitzt.

* Die Werte werden als **kontrollierte Wertelisten** definiert, damit sie konsistent für Filter, Suche und Auswertungen verwendet werden können.

* Ein Ensemble kann **mehrere Rollen und Profile gleichzeitig** besitzen.

#### Beispiel

```json
{
  "id": "beethoven-orchester-bonn",
  "name": "Beethoven Orchester Bonn",

  "type": "orchestra",
  "professional": true,

  "roles": [
    "symphony_orchestra",
    "opera_orchestra"
  ],

  "musicalProfiles": [
    "classical",
    "romantic",
    "contemporary",
    "opera"
  ]
}
```

Ein Ensemble für Alte Musik könnte dagegen so beschrieben werden:

```json
{
  "id": "example-early-music-ensemble",
  "name": "Beispielensemble",

  "type": "ensemble",
  "professional": true,

  "musicalProfiles": [
    "early_music",
    "baroque",
    "historically_informed_performance"
  ]
}
```

**Ziel:** Das Datenmodell soll nicht auf Sinfonieorchester beschränkt sein, sondern die Grundlage für die spätere Aufnahme von **Orchestern, Kammerorchestern, Big Bands, Chören, Vokalensembles und spezialisierten Ensembles** bilden.
