"""Crop health checks and cross-school comparison (the 'shared dashboard' logic)."""
from statistics import mean

from .models import CROP_THRESHOLDS

METRICS = ("moisture", "ph", "temp_c", "ec")


def health_alerts(reading):
    """List of human-readable alerts for a reading dict; empty means healthy."""
    limits = CROP_THRESHOLDS.get(reading["crop"])
    if not limits:
        return []
    alerts = []
    for metric in METRICS:
        lo, hi = limits[metric]
        value = reading[metric]
        if value < lo:
            alerts.append(f"{metric} low ({value} < {lo})")
        elif value > hi:
            alerts.append(f"{metric} high ({value} > {hi})")
    return alerts


def summarize(readings):
    """Average each metric over a list of reading dicts."""
    if not readings:
        return {}
    return {m: round(mean(r[m] for r in readings), 2) for m in METRICS}


def compare(readings_a, readings_b):
    """Metric-wise averages for two schools plus the difference (a - b)."""
    a, b = summarize(readings_a), summarize(readings_b)
    if not a or not b:
        raise ValueError("both schools need at least one reading")
    return {"a": a, "b": b, "diff": {m: round(a[m] - b[m], 2) for m in METRICS}}


def impact_metrics(conn):
    """Program-level numbers mirroring the proposal's dashboard."""
    schools = conn.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
    states = conn.execute("SELECT COUNT(DISTINCT state) FROM schools").fetchone()[0]
    readings = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    return {"schools": schools, "states": states, "readings": readings}
