# Krishi Shala

Open-source reference implementation of **Krishi Shala**: agriculture taught in schools and
colleges as a hands-on, data-driven, career-linked subject, with every institution connected
through one shared "digital twin farm" network.

> **Status: prototype (v0.1).** This repo implements the core data and advice layer using only
> the Python standard library, so it runs anywhere with no installs. Sensors, the Bhashini voice
> layer, and market integrations are defined as clear extension points (see
> [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)). It uses synthetic sample data only.

## What is implemented

| Proposal element | Where | Status |
|---|---|---|
| Farms for rural, urban and landless schools and colleges | `models.FARM_TYPES`, `data/sample_schools.json` | Implemented |
| Sensor data into a shared dashboard | `ingest.py`, `db.py`, `api.py` (`POST /readings`) | Implemented (validated ingest, SQLite) |
| Compare a school with one in another state | `analytics.compare`, `GET /compare` | Implemented |
| Crop health alerts from live data | `analytics.health_alerts` | Implemented (illustrative thresholds) |
| Regional-language AI helper | `advisor.py` (en, ta, hi) | Rule-based baseline; Bhashini adapter is a stub |
| What to plant this month | `advisor.what_to_plant` | Implemented (simple season table) |
| Impact dashboard numbers | `analytics.impact_metrics`, `GET /metrics` | Implemented (schools, states, readings) |
| Syllabus links, FPO/e-NAM, KVK mentor matching | n/a | Roadmap (see architecture doc) |

## Quick start

Requires Python 3.9+ and nothing else.

```bash
git clone <your-repo-url> krishi-shala
cd krishi-shala

# 1. Run the tests
python -m unittest discover -s tests -v

# 2. Load sample schools and readings into a local SQLite file
python -m krishishala.cli load

# 3. Compare the Chennai and Punjab schools
python -m krishishala.cli compare 1 2

# 4. Start the API
python -m krishishala.cli serve --port 8000
```

Try it from another terminal:

```bash
curl localhost:8000/health
curl localhost:8000/schools
curl localhost:8000/metrics
curl "localhost:8000/compare?a=1&b=2"
curl "localhost:8000/plant?month=7"
curl -G localhost:8000/advice --data-urlencode "q=Why are my leaves turning yellow?" \
     --data-urlencode "lang=ta" --data-urlencode "school_id=1"
curl -X POST localhost:8000/readings -H "Content-Type: application/json" \
     -d '{"school_id":3,"ts":"2026-10-20T08:00:00","crop":"spinach","moisture":60,"ph":6.5,"temp_c":22,"ec":1.7}'
```

## API summary

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/schools` | List registered institutions |
| GET | `/metrics` | Schools, states and readings counts |
| GET | `/compare?a=ID&b=ID` | Average metrics for two schools and the difference |
| GET | `/advice?q=TEXT&lang=ta&school_id=ID` | Multilingual advice plus sensor alerts from the school's latest reading |
| GET | `/plant?month=1-12` | Crops suited to sow that month |
| POST | `/readings` | Submit a sensor reading (validated) |

## Sensor reading format

```json
{"school_id": 1, "ts": "2026-10-01T08:00:00", "crop": "tomato",
 "moisture": 55, "ph": 6.4, "temp_c": 28, "ec": 2.2}
```

Values outside physical sensor ranges (for example moisture over 100%) are rejected as sensor
faults rather than stored as crop problems.

## Sample data

`data/` holds four fictional institutions and 14 days of **synthetic** readings each, generated
by `scripts/generate_sample_data.py` (fixed random seed). Two deliberately invalid rows are
included to demonstrate validation. No real student or school data is used.

## Project layout

```
krishishala/   models, db, ingest, analytics, advisor, api, cli
tests/         22 unit and API tests (unittest)
data/          sample schools and readings
docs/          ARCHITECTURE.md
scripts/       sample data generator
```

## Limitations (please read)

- Crop thresholds and planting seasons are **illustrative defaults**, not agronomic advice. They
  must be validated and localised with KVK / ICAR / state agricultural university experts.
- The advisor is keyword rules, not a trained model; the Bhashini integration is a stub.
- The HTTP server is for demos. Use a production framework, authentication and HTTPS before
  any real deployment, and follow child-data-protection rules (India's DPDP Act, 2023) for
  student data.
- Related work already exists (school gardens, ICAR precision-agriculture programmes, e-NAM,
  ed-tech agriculture platforms). The contribution here is the integrated school-to-college
  network, not any single feature.

## Contributing

Issues and pull requests are welcome, especially from agronomists, teachers and
Indian-language speakers (translations in `advisor.ADVICE`). Run the tests before opening a PR.

## License

MIT, see [LICENSE](LICENSE).
