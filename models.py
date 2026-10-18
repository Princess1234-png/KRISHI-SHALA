"""Plain data models and crop thresholds used across the project."""
from dataclasses import dataclass

FARM_TYPES = ("field", "terrace", "vertical", "hydroponic", "agri_lab")

# (min, max) healthy ranges per crop. Illustrative defaults: tune with local KVK advice.
CROP_THRESHOLDS = {
    "tomato":  {"moisture": (40, 70), "ph": (6.0, 6.8), "temp_c": (18, 30), "ec": (1.5, 3.0)},
    "wheat":   {"moisture": (30, 60), "ph": (6.0, 7.5), "temp_c": (10, 25), "ec": (0.5, 2.0)},
    "rice":    {"moisture": (60, 90), "ph": (5.5, 7.0), "temp_c": (20, 35), "ec": (0.5, 2.5)},
    "spinach": {"moisture": (50, 75), "ph": (6.0, 7.0), "temp_c": (10, 24), "ec": (1.2, 2.2)},
}


@dataclass(frozen=True)
class School:
    id: int
    name: str
    state: str
    district: str
    language: str      # ISO 639-1 code: en, ta, hi ...
    farm_type: str


@dataclass(frozen=True)
class Reading:
    school_id: int
    ts: str            # ISO-8601 timestamp
    crop: str
    moisture: float    # soil moisture, %
    ph: float
    temp_c: float
    ec: float          # electrical conductivity, mS/cm (nutrient strength)
