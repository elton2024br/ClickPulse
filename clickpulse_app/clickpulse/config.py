import json


DEFAULTS = {
    "pause_threshold_minutes": 3,
    "activity_check_seconds": 10,
    "notification_click_milestone": 100,
    "long_pause_alert_minutes": 30,
}


class Config:
    def __init__(self, database):
        self._db = database
        for key, value in DEFAULTS.items():
            if self._db.get_setting(key) is None:
                self._db.set_setting(key, json.dumps(value))
        self._cleanup_legacy_keys()

    def get(self, key, default=None):
        raw = self._db.get_setting(key)
        if raw is None:
            return default
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return default

    def set(self, key, value):
        self._db.set_setting(key, json.dumps(value))

    @property
    def pause_threshold_minutes(self):
        return self.get("pause_threshold_minutes", DEFAULTS["pause_threshold_minutes"])

    @property
    def activity_check_seconds(self):
        return self.get("activity_check_seconds", DEFAULTS["activity_check_seconds"])

    @property
    def notification_click_milestone(self):
        return self.get("notification_click_milestone", DEFAULTS["notification_click_milestone"])

    @property
    def long_pause_alert_minutes(self):
        return self.get("long_pause_alert_minutes", DEFAULTS["long_pause_alert_minutes"])

    def _cleanup_legacy_keys(self):
        legacy_keys = ["console_refresh_seconds"]
        for key in legacy_keys:
            if self._db.get_setting(key) is not None:
                self._db.delete_setting(key)

    def reset_defaults(self):
        for key, value in DEFAULTS.items():
            self.set(key, value)
