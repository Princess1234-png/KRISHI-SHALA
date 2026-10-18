import unittest

from krishishala import db, ingest

GOOD = {"school_id": 1, "ts": "2026-10-01T08:00:00", "crop": "Tomato",
        "moisture": 55, "ph": 6.4, "temp_c": 28, "ec": 2.2}


class IngestTests(unittest.TestCase):
    def test_valid_reading_normalises_crop(self):
        self.assertEqual(ingest.validate_reading(GOOD).crop, "tomato")

    def test_missing_field(self):
        bad = dict(GOOD)
        del bad["ph"]
        with self.assertRaisesRegex(ValueError, "missing field: ph"):
            ingest.validate_reading(bad)

    def test_out_of_range_sensor_value(self):
        with self.assertRaisesRegex(ValueError, "outside sensor range"):
            ingest.validate_reading({**GOOD, "moisture": 250})

    def test_unknown_crop_and_bad_timestamp(self):
        with self.assertRaises(ValueError):
            ingest.validate_reading({**GOOD, "crop": "banana"})
        with self.assertRaises(ValueError):
            ingest.validate_reading({**GOOD, "ts": "yesterday"})

    def test_sample_data_loads_and_rejects_bad_rows(self):
        conn = db.connect()
        ingest.load_schools(conn, "data/sample_schools.json")
        loaded, rejected = ingest.load_readings_csv(conn, "data/sample_readings.csv")
        self.assertEqual(loaded, 56)
        self.assertEqual(rejected, 2)
        self.assertEqual(len(db.list_schools(conn)), 4)


if __name__ == "__main__":
    unittest.main()
