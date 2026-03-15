from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer


class SystemTray(QSystemTrayIcon):
    def __init__(self, window, tracker, activity, aggregator, icon_path=None):
        super().__init__()
        self._window = window
        self._tracker = tracker
        self._activity = activity
        self._aggregator = aggregator

        if icon_path:
            self.setIcon(QIcon(icon_path))
        else:
            self.setIcon(window.windowIcon())

        self._update_tooltip()

        menu = QMenu()

        open_action = QAction("Abrir ClickPulse", menu)
        open_action.triggered.connect(self._show_window)
        menu.addAction(open_action)

        self._pause_action = QAction("Pausar rastreamento", menu)
        self._pause_action.triggered.connect(self._toggle_tracking)
        menu.addAction(self._pause_action)

        menu.addSeparator()

        quit_action = QAction("Sair", menu)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

        self._tooltip_timer = QTimer()
        self._tooltip_timer.timeout.connect(self._update_tooltip)
        self._tooltip_timer.start(30_000)

    def _show_window(self):
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()

    def _toggle_tracking(self):
        if self._tracker.is_paused:
            self._tracker.resume()
            self._pause_action.setText("Pausar rastreamento")
            self._window.update_tracking_state(True)
        else:
            self._tracker.pause()
            self._pause_action.setText("Retomar rastreamento")
            self._window.update_tracking_state(False)

    def _quit_app(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _update_tooltip(self):
        try:
            rate = self._aggregator.get_current_hour_clicks()
            state = "Ativo" if self._activity.current_state == "active" else "Pausa"
            self.setToolTip(f"ClickPulse — {rate} cliques/hora | {state}")
        except Exception:
            self.setToolTip("ClickPulse")

    def update_pause_action_text(self, is_tracking):
        if is_tracking:
            self._pause_action.setText("Pausar rastreamento")
        else:
            self._pause_action.setText("Retomar rastreamento")
