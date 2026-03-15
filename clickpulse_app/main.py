"""ClickPulse — Entry point."""

import sys
import signal
import os
import tempfile
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QLockFile
from PyQt6.QtGui import QIcon

from clickpulse.database import Database
from clickpulse.config import Config
from clickpulse.tracker import MouseTracker
from clickpulse.activity import ActivityDetector
from clickpulse.aggregator import Aggregator
from clickpulse.notifier import Notifier
from clickpulse.ui.main_window import MainWindow
from clickpulse.ui.tray import SystemTray


def get_app_dir():
    return os.path.dirname(os.path.abspath(__file__))


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("ClickPulse")

    lock_path = os.path.join(tempfile.gettempdir(), "clickpulse.lock")
    lock_file = QLockFile(lock_path)
    if not lock_file.tryLock(100):
        QMessageBox.warning(
            None,
            "ClickPulse",
            "O ClickPulse ja esta em execucao.\nVerifique a bandeja do sistema.",
        )
        sys.exit(0)

    app_dir = get_app_dir()
    icon_path = os.path.join(app_dir, "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    db_path = os.path.join(app_dir, "clickpulse.db")
    db = Database(db_path)
    config = Config(db)
    notifier = Notifier()
    aggregator = Aggregator(db)

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    counts = db.count_clicks_in_range(today, tomorrow)
    notifier.initialize_milestone(counts["total"], config)

    tracker = MouseTracker(db)
    activity = ActivityDetector(db, config, tracker)

    window = MainWindow(db, config, tracker, activity, aggregator)
    tray = SystemTray(window, tracker, activity, aggregator, icon_path if os.path.exists(icon_path) else None)

    tracker.start()
    activity.start()

    last_aggregated_hour = [datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)]

    hourly_timer = QTimer()
    def check_hourly():
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        prev_hour = current_hour - timedelta(hours=1)
        if prev_hour > last_aggregated_hour[0]:
            aggregator.aggregate_hour(prev_hour)
            last_aggregated_hour[0] = prev_hour
            stats = db.get_hourly_stats(prev_hour.strftime("%Y-%m-%d"))
            for s in stats:
                try:
                    h = datetime.strptime(s["hour_start"], "%Y-%m-%d %H:%M:%S")
                    if h == prev_hour:
                        notifier.hourly_summary(s)
                        break
                except (ValueError, TypeError):
                    pass
    hourly_timer.timeout.connect(check_hourly)
    hourly_timer.start(60_000)

    refresh_timer = QTimer()
    refresh_timer.timeout.connect(window.refresh_dashboard)
    refresh_timer.start(5_000)

    notify_timer = QTimer()
    def check_notifications():
        t = datetime.now().strftime("%Y-%m-%d")
        tm = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        c = db.count_clicks_in_range(t, tm)
        notifier.check_milestones(c["total"], config)
        if activity.current_state == "pause":
            notifier.check_long_pause(activity.current_pause_duration, config)
    notify_timer.timeout.connect(check_notifications)
    notify_timer.start(30_000)

    window.show()
    tray.show()

    def shutdown():
        tracker.stop()
        activity.stop()
        aggregator.aggregate_previous_hour()
        db.close()
        lock_file.unlock()

    app.aboutToQuit.connect(shutdown)
    signal.signal(signal.SIGINT, lambda *_: app.quit())

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
