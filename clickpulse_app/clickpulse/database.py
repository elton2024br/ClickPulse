import sqlite3
import threading
from datetime import datetime


class Database:
    def __init__(self, db_path="clickpulse.db"):
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._init_tables()

    def _init_tables(self):
        with self._lock:
            cur = self._conn.cursor()
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
                    button TEXT NOT NULL CHECK(button IN ('left', 'right', 'middle')),
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_clicks_timestamp ON clicks(timestamp);

                CREATE TABLE IF NOT EXISTS activity_periods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    type TEXT NOT NULL CHECK(type IN ('active', 'pause'))
                );
                CREATE INDEX IF NOT EXISTS idx_activity_start ON activity_periods(start_time);

                CREATE TABLE IF NOT EXISTS hourly_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hour_start DATETIME NOT NULL UNIQUE,
                    total_clicks INTEGER NOT NULL DEFAULT 0,
                    left_clicks INTEGER NOT NULL DEFAULT 0,
                    right_clicks INTEGER NOT NULL DEFAULT 0,
                    middle_clicks INTEGER NOT NULL DEFAULT 0,
                    active_seconds INTEGER NOT NULL DEFAULT 0,
                    pause_seconds INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_hourly_start ON hourly_stats(hour_start);

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            self._conn.commit()

    def insert_click(self, button, x, y):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO clicks (button, x, y) VALUES (?, ?, ?)",
                (button, x, y),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_clicks_since(self, since):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "SELECT * FROM clicks WHERE timestamp >= ? ORDER BY timestamp",
                (since,),
            )
            return [dict(row) for row in cur.fetchall()]

    def get_clicks_in_range(self, start, end):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "SELECT * FROM clicks WHERE timestamp >= ? AND timestamp < ? ORDER BY timestamp",
                (start, end),
            )
            return [dict(row) for row in cur.fetchall()]

    def count_clicks_in_range(self, start, end):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                """SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN button='left' THEN 1 ELSE 0 END) as left_clicks,
                    SUM(CASE WHEN button='right' THEN 1 ELSE 0 END) as right_clicks,
                    SUM(CASE WHEN button='middle' THEN 1 ELSE 0 END) as middle_clicks
                FROM clicks WHERE timestamp >= ? AND timestamp < ?""",
                (start, end),
            )
            row = cur.fetchone()
            return {
                "total": row["total"] or 0,
                "left_clicks": row["left_clicks"] or 0,
                "right_clicks": row["right_clicks"] or 0,
                "middle_clicks": row["middle_clicks"] or 0,
            }

    def insert_activity_period(self, start_time, type_, end_time=None):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO activity_periods (start_time, type, end_time) VALUES (?, ?, ?)",
                (start_time, type_, end_time),
            )
            self._conn.commit()
            return cur.lastrowid

    def close_activity_period(self, period_id, end_time):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "UPDATE activity_periods SET end_time = ? WHERE id = ?",
                (end_time, period_id),
            )
            self._conn.commit()

    def get_open_period(self):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "SELECT * FROM activity_periods WHERE end_time IS NULL ORDER BY id DESC LIMIT 1"
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def get_activity_periods_in_range(self, start, end):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                """SELECT * FROM activity_periods
                WHERE (start_time < ? AND (end_time > ? OR end_time IS NULL))
                ORDER BY start_time""",
                (end, start),
            )
            return [dict(row) for row in cur.fetchall()]

    def upsert_hourly_stats(self, hour_start, total, left, right, middle, active_sec, pause_sec):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                """INSERT INTO hourly_stats
                    (hour_start, total_clicks, left_clicks, right_clicks, middle_clicks, active_seconds, pause_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(hour_start) DO UPDATE SET
                    total_clicks=excluded.total_clicks,
                    left_clicks=excluded.left_clicks,
                    right_clicks=excluded.right_clicks,
                    middle_clicks=excluded.middle_clicks,
                    active_seconds=excluded.active_seconds,
                    pause_seconds=excluded.pause_seconds""",
                (hour_start, total, left, right, middle, active_sec, pause_sec),
            )
            self._conn.commit()

    def get_hourly_stats(self, date_str):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                """SELECT * FROM hourly_stats
                WHERE hour_start >= ? AND hour_start < datetime(?, '+1 day')
                ORDER BY hour_start""",
                (date_str, date_str),
            )
            return [dict(row) for row in cur.fetchall()]

    def get_setting(self, key, default=None):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default

    def set_setting(self, key, value):
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
            self._conn.commit()

    def close(self):
        with self._lock:
            self._conn.close()
