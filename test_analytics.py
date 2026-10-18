import unittest

from krishishala import analytics, db, ingest


def reading(**kw):
    base = {"crop": "tomato", "moisture": 55, "ph": 6.4, "temp_c": 25, "ec": 2.0}
    base.update(kw)
    return base


class AnalyticsTests(unittest.TestCase):
    def test_healthy_reading_has_no_alerts(self):
        self.assertEqual(analytics.health_alerts(reading()), [])

    def test_low_moisture_and_high_ph_alerts(self):
        alerts = analytics.health_alerts(reading(moisture=20, ph=8.0))
        self.assertEqual(len(alerts), 2)
        self.assertTrue(any("moisture low" in a for a in alerts))
        self.assertTrue(any("ph high" in a for a in alerts))

    def test_compare_difference(self):
        result = analytics.compare([reading(moisture=60)], [reading(moisture=40)])
        self.assertEqual(result["diff"]["moisture"], 20)

    def test_compare_needs_data(self):
        with self.assertRaises(ValueError):
            analytics.compare([], [reading()])

    def test_impact_metrics_on_sample_data(self):
        conn = db.connect()
        ingest.load_schools(conn, "data/sample_schools.json")
        ingest.load_readings_csv(conn, "data/sample_readings.csv")
        m = analytics.impact_metrics(conn)
        self.assertEqual((m["schools"], m["states"], m["readings"]), (4, 3, 56))


if __name__ == "__main__":
    unittest.main()
