"""Deterministically generate synthetic sensor data (no real student data)."""
import csv
import random
from datetime import datetime, timedelta

random.seed(42)
PROFILES = {  # school_id: (crop, moisture, ph, temp_c, ec)
    1: ("tomato", 55, 6.4, 28, 2.2),
    2: ("wheat", 45, 6.8, 20, 1.2),
    3: ("spinach", 60, 6.5, 22, 1.7),
    4: ("rice", 75, 6.2, 29, 1.5),
}
start = datetime(2026, 10, 1)
with open("data/sample_readings.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["school_id", "ts", "crop", "moisture", "ph", "temp_c", "ec"])
    for sid, (crop, m, ph, t, ec) in PROFILES.items():
        for day in range(14):
            ts = (start + timedelta(days=day, hours=8)).isoformat()
            w.writerow([sid, ts, crop, round(m + random.uniform(-8, 8), 1),
                        round(ph + random.uniform(-0.4, 0.4), 2),
                        round(t + random.uniform(-3, 3), 1),
                        round(ec + random.uniform(-0.3, 0.3), 2)])
    # Deliberately bad rows so the validator is exercised.
    w.writerow([1, "2026-10-15T08:00:00", "tomato", 250, 6.4, 28, 2.2])
    w.writerow([2, "not-a-date", "wheat", 45, 6.8, 20, 1.2])
