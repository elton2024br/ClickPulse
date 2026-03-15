import threading
from datetime import datetime, timedelta


class ActivityDetector:
    def __init__(self, database, config, tracker):
        self._db = database
        self._config = config
        self._tracker = tracker
        self._running = False
        self._thread = None
        self._state = "active"
        self._current_period_id = None
        self._current_pause_start = None

    def start(self):
        if self._running:
            return
        self._running = True
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._current_period_id = self._db.insert_activity_period(now, "active")
        self._state = "active"
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._current_period_id is not None:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._db.close_activity_period(self._current_period_id, now)

    def _check_loop(self):
        while self._running:
            try:
                self._check_activity()
            except Exception:
                pass
            interval = self._config.activity_check_seconds
            for _ in range(int(interval * 10)):
                if not self._running:
                    return
                threading.Event().wait(0.1)

    def _check_activity(self):
        now = datetime.now()
        idle_time = now - self._tracker.last_activity_time
        threshold = timedelta(minutes=self._config.pause_threshold_minutes)

        if idle_time >= threshold and self._state == "active":
            last_active = self._tracker.last_activity_time.strftime("%Y-%m-%d %H:%M:%S")
            if self._current_period_id is not None:
                self._db.close_activity_period(self._current_period_id, last_active)
            self._current_period_id = self._db.insert_activity_period(last_active, "pause")
            self._current_pause_start = self._tracker.last_activity_time
            self._state = "pause"

        elif idle_time < threshold and self._state == "pause":
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            if self._current_period_id is not None:
                self._db.close_activity_period(self._current_period_id, now_str)
            self._current_period_id = self._db.insert_activity_period(now_str, "active")
            self._current_pause_start = None
            self._state = "active"

    @property
    def current_state(self):
        return self._state

    @property
    def current_pause_duration(self):
        if self._state == "pause" and self._current_pause_start:
            return datetime.now() - self._current_pause_start
        return timedelta(0)

    @property
    def active_time_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        periods = self._db.get_activity_periods_in_range(today, tomorrow)
        total = timedelta(0)
        for p in periods:
            if p["type"] == "active":
                start = datetime.strptime(p["start_time"], "%Y-%m-%d %H:%M:%S")
                if p["end_time"]:
                    end = datetime.strptime(p["end_time"], "%Y-%m-%d %H:%M:%S")
                else:
                    end = datetime.now()
                total += end - start
        return total

    @property
    def pause_time_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        periods = self._db.get_activity_periods_in_range(today, tomorrow)
        total = timedelta(0)
        for p in periods:
            if p["type"] == "pause":
                start = datetime.strptime(p["start_time"], "%Y-%m-%d %H:%M:%S")
                if p["end_time"]:
                    end = datetime.strptime(p["end_time"], "%Y-%m-%d %H:%M:%S")
                else:
                    end = datetime.now()
                total += end - start
        return total
