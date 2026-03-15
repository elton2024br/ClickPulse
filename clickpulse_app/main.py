"""ClickPulse — Entry point."""

import sys
import signal
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon

from clickpulse.database import Database
from clickpulse.config import Config
from clickpulse.tracker import MouseTracker
from clickpulse.activity import ActivityDetector
from clickpulse.aggregator import Aggregator
from clickpulse.notifier import Notifier
from clickpulse.ui.main_window import MainWindow
from clickpulse.ui.tray import SystemTray


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("ClickPulse")

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    db = Database("clickpulse.db")
    config = Config(db)
    notifier = Notifier()
    aggregator = Aggregator(db)

    tracker = MouseTracker(db)
    activity = ActivityDetector(db, config, tracker)

    window = MainWindow(db, config, tracker, activity, aggregator)
    tray = SystemTray(window, tracker, activity, icon_path if os.path.exists(icon_path) else None)

    tracker.start()
    activity.start()

    hourly_timer = QTimer()
    hourly_timer.timeout.connect(aggregator.aggregate_previous_hour)
    hourly_timer.start(60_000)

    refresh_timer = QTimer()
    refresh_timer.timeout.connect(window.refresh_dashboard)
    refresh_timer.start(5_000)

    notify_timer = QTimer()
    def check_notifications():
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        counts = db.count_clicks_in_range(today, tomorrow)
        notifier.check_milestones(counts["total"], config)
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

    app.aboutToQuit.connect(shutdown)
    signal.signal(signal.SIGINT, lambda *_: app.quit())

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
