"""Minimal JSON HTTP API (standard library only).

GET  /health
GET  /schools
GET  /metrics
GET  /compare?a=1&b=3
GET  /advice?q=yellow+leaves&lang=ta&school_id=1
GET  /plant?month=7
POST /readings   (JSON body)
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import advisor, analytics, db
from .ingest import validate_reading


def make_handler(conn):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # keep test/server output quiet
            pass

        def do_GET(self):
            url = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            try:
                if url.path == "/health":
                    return self._send(200, {"status": "ok"})
                if url.path == "/schools":
                    return self._send(200, db.list_schools(conn))
                if url.path == "/metrics":
                    return self._send(200, analytics.impact_metrics(conn))
                if url.path == "/compare":
                    a, b = int(q["a"]), int(q["b"])
                    return self._send(200, analytics.compare(db.readings_for(conn, a), db.readings_for(conn, b)))
                if url.path == "/advice":
                    latest = db.latest_reading(conn, int(q["school_id"])) if "school_id" in q else None
                    return self._send(200, advisor.advise(q.get("q", ""), q.get("lang", "en"), latest))
                if url.path == "/plant":
                    return self._send(200, {"crops": advisor.what_to_plant(int(q["month"]))})
            except (KeyError, ValueError) as exc:
                return self._send(400, {"error": f"bad request: {exc}"})
            self._send(404, {"error": "not found"})

        def do_POST(self):
            if urlparse(self.path).path != "/readings":
                return self._send(404, {"error": "not found"})
            try:
                length = int(self.headers.get("Content-Length", 0))
                reading = validate_reading(json.loads(self.rfile.read(length)))
                if not db.get_school(conn, reading.school_id):
                    return self._send(404, {"error": "unknown school_id"})
                db.add_reading(conn, reading)
            except (ValueError, json.JSONDecodeError) as exc:
                return self._send(400, {"error": str(exc)})
            self._send(201, {"status": "stored"})

    return Handler


def make_server(conn, host="127.0.0.1", port=8000):
    return ThreadingHTTPServer((host, port), make_handler(conn))
