# Komponist:innen und Werke (`composers.json`, `works.json`)

## Zweck

`composers` und `works` bilden die musikalischen Stammdaten. Ein `work` beantwortet die
Frage „Was ist das Werk?“, ein `composer` „Wer hat es geschrieben?“. Beide enthalten
**keine** Aufführungsdaten – wann und wie ein Werk gespielt wird, steht ausschließlich im
Programm eines Events (siehe [events-and-relations.md](../events-and-relations.md)). Ein
Werk kann dadurch in beliebig vielen Events vorkommen.

Dieses Dokument ergänzt die im [events-and-relations.md](../events-and-relations.md)
beschriebene Programm-/Werk-Trennung um die vollständige Feldbeschreibung der Stammdaten.

---

## Komponist:innen (`composers.json`)

### Beispiel

```json
{
  "id": "gustav-mahler",
  "name": "Gustav Mahler",
  "life": { "from": 1860, "to": 1911 }
}
```

### Felder

| Feld | Pflicht | Typ | Bedeutung |
| --- | --- | --- | --- |
| `id` | ja | string | Stabile Klangland-ID (`kebab-case`). |
| `name` | ja | string | Vollständiger Name inkl. Diakritika. |
| `life` | ja | object | Lebensdaten `{ "from": <Geburtsjahr>, "to": <Todesjahr> }`; `to` darf `null` sein (lebende Person). |

### Beziehungen

- **Work → Composer:** [`works.composerId`](#werke-worksjson) → `composers.id`.
  Ein:e Komponist:in kann mehrere Werke haben.

---

## Werke (`works.json`)

### Beispiel

```json
{
  "id": "bruckner-sinfonie-7",
  "composerId": "anton-bruckner",
  "title": "Sinfonie Nr. 7 E-Dur",
  "catalogue": [{ "system": "WAB", "number": "107" }],
  "yearComposed": { "from": 1881, "to": 1883 },
  "genre": "symphony",
  "durationMinutes": 65,
  "version": null,
  "scoring": null,
  "description": null
}
```

### Felder

| Feld | Pflicht | Typ | Bedeutung |
| --- | --- | --- | --- |
| `id` | ja | string | Stabile Klangland-ID (`kebab-case`). |
| `composerId` | ja | string | Referenz auf [`composers.id`](#komponistinnen-composersjson). |
| `title` | ja | string | Werktitel inkl. Tonart (z. B. `Sinfonie Nr. 5 c-Moll`). |
| `catalogue` | ja | array | Liste von Katalogeinträgen `{ "system", "number" }`; leer `[]`, wenn keiner existiert. |
| `yearComposed` | ja | object | Entstehungszeitraum `{ "from", "to" }`; einzelnes Jahr → `from == to`. |
| `genre` | ja | enum | Gattung (kontrollierter Wert). |
| `durationMinutes` | ja | number \| null | Ungefähre **Werksdauer** (nicht Konzertdauer). |
| `version` | ja | string \| null | Werkfassung, falls relevant. |
| `scoring` | ja | string \| null | Besetzung, falls erfasst. |
| `description` | ja | string \| null | Kurzbeschreibung. |

### Katalog (`catalogue`)

Katalognummern werden als Liste modelliert, weil ein Werk mehrere Zählsysteme haben kann.

| `system` (Beispiele) | Bedeutung |
| --- | --- |
| `Opus` | Opuszahl |
| `KV` | Köchelverzeichnis (Mozart) |
| `D` | Deutsch-Verzeichnis (Schubert) |
| `WAB` | Werkverzeichnis Anton Bruckner |
| `BWV` | Bach-Werke-Verzeichnis |

### Kontrollierte Werte: `genre`

`symphony`, `concerto`, `overture`, `opera`, `oratorio`, `requiem`, `chamber_music`,
`other`. Weitere Werte werden bei Bedarf ergänzt.

### Beziehungen

- **Work → Composer:** `composerId` → `composers.id`.
- **Event → Work:** [`events.program[].workId`](../events-and-relations.md) verweist auf
  ein Werk. Ein optional aufgeführter Satz (`movement`/`movements`) oder eine Fassung
  (`version`) wird **im Event** angegeben, nicht im Werk – dieselbe Werksdefinition kann so
  in verschiedenen Events unterschiedlich (voll/teilweise) aufgeführt werden.

## Pflege und Validierung

- `id` je Datei eindeutig.
- `works.composerId` existiert in `composers.json`.
- `genre` und `catalogue[].system` verwenden kontrollierte Werte.
- `yearComposed.from ≤ yearComposed.to`; bei `composers.life` analog, sofern `to` gesetzt.
- Jeder von Events referenzierte `workId` existiert in `works.json`.
