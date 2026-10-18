"""Validation and loading of sensor readings and school records."""
import csv
import json
from datetime import datetime

from . import db
from .models import CROP_THRESHOLDS, FARM_TYPES, Reading, School

# Physically plausible bounds; anything outside is a sensor fault, not a crop problem.
SANE = {"moisture": (0, 100), "ph": (0, 14), "temp_c": (-5, 60), "ec": (0, 10)}


def validate_reading(data):
    """Return a Reading or raise ValueError with a clear message."""
    try:
        school_id = int(data["school_id"])
        crop = str(data["crop"]).strip().lower()
        ts = str(data["ts"])
        datetime.fromisoformat(ts)
        values = {k: float(data[k]) for k in SANE}
    except KeyError as exc:
        raise ValueError(f"missing field: {exc.args[0]}") from None
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid reading: {exc}") from None
    if crop not in CROP_THRESHOLDS:
        raise ValueError(f"unknown crop: {crop}")
    for key, (lo, hi) in SANE.items():
        if not lo <= values[key] <= hi:
            raise ValueError(f"{key}={values[key]} outside sensor range {lo}..{hi}")
    return Reading(school_id, ts, crop, **values)


def load_schools(conn, path):
    with open(path, encoding="utf-8") as fh:
        for item in json.load(fh):
            if item["farm_type"] not in FARM_TYPES:
                raise ValueError(f"bad farm_type for {item['name']}")
            db.add_school(conn, School(**item))


def load_readings_csv(conn, path):
    """Load readings; returns (loaded, rejected) counts. Bad rows are skipped, not fatal."""
    loaded = rejected = 0
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                db.add_reading(conn, validate_reading(row))
                loaded += 1
            except ValueError:
                rejected += 1
    return loaded, rejected
