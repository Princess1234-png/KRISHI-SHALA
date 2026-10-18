# Architecture

## Goals

1. Let any institution, with land or without, join one network and share comparable farm data.
2. Give students guidance in their own language.
3. Keep the prototype dependency-free so schools and contributors can run it easily.
4. Provide clean seams where national systems (Bhashini, e-NAM, KVK networks) plug in.

## System overview

```
 Farm sensors / manual entry          Students & teachers (web / mobile / voice)
          |                                        |
          v                                        v
   +--------------+      +-----------------------------------------+
   |  Ingest      |      |  HTTP API  (krishishala/api.py)         |
   |  validate    +----->|  /readings /schools /compare /advice    |
   +------+-------+      +----+---------------+--------------------+
          |                   |               |
          v                   v               v
   +--------------+     +-----------+   +-------------------+
   |  SQLite      |<----+ Analytics |   | Advisor           |
   |  schools,    |     | alerts,   |   | rules -> answer   |
   |  readings    |     | compare,  |   | + sensor alerts   |
   +--------------+     | metrics   |   +---------+---------+
                        +-----------+             |
                                                  v
                                       BhashiniAdapter (stub)
                                       ASR -> translate -> TTS
```

## Modules

| Module | Responsibility |
|---|---|
| `models.py` | `School`, `Reading` dataclasses, farm types, per-crop healthy ranges |
| `db.py` | SQLite schema and queries (`schools`, `readings`, index on school and time) |
| `ingest.py` | Validate readings (required fields, ISO timestamp, known crop, sensor range); bulk load CSV/JSON; bad rows are counted and skipped |
| `analytics.py` | Health alerts vs crop ranges, per-school averages, cross-school comparison, programme metrics |
| `advisor.py` | Symptom classification (English, Tamil, Hindi keywords), multilingual answers, seasonal planting, attaches live sensor alerts |
| `api.py` | JSON API on `http.server`; one handler factory bound to a connection |
| `cli.py` | `load`, `serve`, `compare` commands |

## Data model

- `schools(id, name, state, district, language, farm_type)`
- `readings(id, school_id, ts, crop, moisture, ph, temp_c, ec)`

Farm types: `field`, `terrace`, `vertical`, `hydroponic`, `agri_lab`. A landless school can still
participate by studying another school's live readings through `/compare`.

## Key design decisions

- **Standard library only.** Maximises portability for low-resource schools and keeps CI trivial.
- **Validation at the edge.** Sensor faults (impossible values) are rejected at ingest so analytics
  never mixes faults with real crop stress.
- **Rules before ML.** A transparent rule engine is auditable by teachers and agronomists; a model
  can later replace `advisor.classify` behind the same interface.
- **Adapters for national systems.** External services sit behind small classes so the core runs
  offline and secret-free.

## Extension points (roadmap)

| Phase | Item | Approach |
|---|---|---|
| Pilot (50 schools, 5 states) | Real sensors | Add an MQTT/LoRaWAN subscriber that calls `ingest.validate_reading` then `db.add_reading` |
| Pilot | Voice assistant | Implement `BhashiniAdapter` (ASR, translation, TTS) and call it around `advisor.advise` |
| Pilot | Dashboard UI | Static web front end consuming the JSON API |
| Expansion | Mentor matching | New `mentors` table (KVK, ICAR institute, Krishi Guru) matched by district and crop |
| Expansion | Auth and roles | Student, teacher, mentor, admin; per-school data scoping |
| Expansion | Postgres | Replace `db.py` behind the same function signatures |
| Integration | Market links | Adapter for FPO / mandi price feeds and e-NAM listings; ledger of school farm income |
| Integration | Syllabus mapping | Table mapping activities to NEP / Samagra Shiksha vocational competencies and certificates |

## Security and privacy

- Prototype has no authentication. Do not expose it publicly as is.
- Store the minimum about students; prefer school-level data. Obtain verifiable parental consent for
  any child personal data (DPDP Act, 2023) before adding student accounts.
- Keep Bhashini and market-API credentials in environment variables, never in the repo.

## Testing

`python -m unittest discover -s tests -v` runs 22 tests covering validation, analytics,
multilingual advice, sample-data loading and the live HTTP API (started on a free port).
GitHub Actions runs them on Python 3.9 and 3.12 (`.github/workflows/ci.yml`).
