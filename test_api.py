import json
import threading
import unittest
import urllib.error
import urllib.request
from urllib.parse import quote

from krishishala import api, db, ingest


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conn = db.connect()
        ingest.load_schools(conn, "data/sample_schools.json")
        ingest.load_readings_csv(conn, "data/sample_readings.csv")
        cls.server = api.make_server(conn, port=0)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        with urllib.request.urlopen(self.base + path) as resp:
            return resp.status, json.loads(resp.read())

    def test_health_and_schools(self):
        self.assertEqual(self.get("/health"), (200, {"status": "ok"}))
        self.assertEqual(len(self.get("/schools")[1]), 4)

    def test_compare_chennai_vs_punjab(self):
        status, body = self.get("/compare?a=1&b=2")
        self.assertEqual(status, 200)
        self.assertIn("moisture", body["diff"])

    def test_advice_in_tamil_with_live_alerts(self):
        status, body = self.get("/advice?school_id=1&lang=ta&q=" + quote("yellow leaves"))
        self.assertEqual(status, 200)
        self.assertEqual(body["topic"], "yellow_leaves")

    def test_bad_request_is_400(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.get("/compare?a=1")
        self.assertEqual(ctx.exception.code, 400)

    def test_post_reading(self):
        payload = {"school_id": 3, "ts": "2026-10-20T08:00:00", "crop": "spinach",
                   "moisture": 60, "ph": 6.5, "temp_c": 22, "ec": 1.7}
        req = urllib.request.Request(self.base + "/readings", json.dumps(payload).encode(),
                                     {"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 201)

    def test_post_invalid_reading_rejected(self):
        payload = {"school_id": 3, "ts": "2026-10-20T08:00:00", "crop": "spinach",
                   "moisture": 999, "ph": 6.5, "temp_c": 22, "ec": 1.7}
        req = urllib.request.Request(self.base + "/readings", json.dumps(payload).encode())
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
