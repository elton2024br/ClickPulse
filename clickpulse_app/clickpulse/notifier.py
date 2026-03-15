import sys
from datetime import date


class Notifier:
    def __init__(self):
        self._last_milestone = 0
        self._long_pause_notified = False
        self._current_date = date.today()

    def initialize_milestone(self, total_clicks_today, config):
        milestone = config.notification_click_milestone
        if milestone > 0:
            self._last_milestone = total_clicks_today // milestone

    def notify(self, title, message, duration=5):
        try:
            if sys.platform == "win32":
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    timeout=duration,
                    app_name="ClickPulse",
                )
            else:
                print(f"[Notification] {title}: {message}")
        except Exception:
            print(f"[Notification] {title}: {message}")

    def _check_date_rollover(self):
        today = date.today()
        if today != self._current_date:
            self._current_date = today
            self._last_milestone = 0
            self._long_pause_notified = False

    def check_milestones(self, total_clicks_today, config):
        self._check_date_rollover()
        milestone = config.notification_click_milestone
        if milestone <= 0:
            return
        current_level = total_clicks_today // milestone
        if current_level > self._last_milestone and total_clicks_today > 0:
            self._last_milestone = current_level
            self.notify(
                "ClickPulse",
                f"\U0001f3af {total_clicks_today} cliques hoje!",
            )

    def check_long_pause(self, pause_duration, config):
        threshold_minutes = config.long_pause_alert_minutes
        pause_minutes = pause_duration.total_seconds() / 60
        if pause_minutes >= threshold_minutes and not self._long_pause_notified:
            self._long_pause_notified = True
            self.notify(
                "ClickPulse",
                f"\u23f8 Pausa de {int(pause_minutes)} minutos detectada",
            )
        elif pause_minutes < threshold_minutes:
            self._long_pause_notified = False

    def hourly_summary(self, hour_stats):
        if not hour_stats:
            return
        clicks = hour_stats.get("total_clicks", 0)
        active_min = hour_stats.get("active_seconds", 0) // 60
        self.notify(
            "ClickPulse",
            f"\u23f0 \u00daltima hora: {clicks} cliques, {active_min} min ativo",
        )

    def reset_daily(self):
        self._last_milestone = 0
        self._long_pause_notified = False
