"""SQLite storage layer (standard library only)."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS schools (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, state TEXT NOT NULL,
    district TEXT NOT NULL, language TEXT NOT NULL, farm_type TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    ts TEXT NOT NULL, crop TEXT NOT NULL,
    moisture REAL, ph REAL, temp_c REAL, ec REAL
);
CREATE INDEX IF NOT EXISTS idx_readings_school_ts ON readings(school_id, ts);
"""


def connect(path=":memory:"):
    # check_same_thread=False so the demo HTTP server can share one connection.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def add_school(conn, school):
    conn.execute(
        "INSERT OR REPLACE INTO schools VALUES (?,?,?,?,?,?)",
        (school.id, school.name, school.state, school.district, school.language, school.farm_type),
    )
    conn.commit()


def add_reading(conn, r):
    conn.execute(
        "INSERT INTO readings (school_id, ts, crop, moisture, ph, temp_c, ec) VALUES (?,?,?,?,?,?,?)",
        (r.school_id, r.ts, r.crop, r.moisture, r.ph, r.temp_c, r.ec),
    )
    conn.commit()


def list_schools(conn):
    return [dict(row) for row in conn.execute("SELECT * FROM schools ORDER BY id")]


def get_school(conn, school_id):
    row = conn.execute("SELECT * FROM schools WHERE id=?", (school_id,)).fetchone()
    return dict(row) if row else None


def latest_reading(conn, school_id):
    row = conn.execute(
        "SELECT * FROM readings WHERE school_id=? ORDER BY ts DESC, id DESC LIMIT 1", (school_id,)
    ).fetchone()
    return dict(row) if row else None


def readings_for(conn, school_id):
    return [dict(r) for r in conn.execute(
        "SELECT * FROM readings WHERE school_id=? ORDER BY ts", (school_id,))]
