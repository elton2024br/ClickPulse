import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QToolBar, QStatusBar,
    QFileDialog, QMessageBox,
)
from PyQt6.QtGui import QIcon, QAction, QFont
from PyQt6.QtCore import Qt

from clickpulse.ui.dashboard import DashboardWidget
from clickpulse.ui.history import HistoryWidget
from clickpulse.ui.settings_ui import SettingsWidget
from clickpulse.exporter import Exporter


class MainWindow(QMainWindow):
    def __init__(self, database, config, tracker, activity, aggregator):
        super().__init__()
        self._db = database
        self._config = config
        self._tracker = tracker
        self._activity = activity
        self._aggregator = aggregator
        self._is_tracking = True

        self.setWindowTitle("ClickPulse — Mouse Activity Tracker")
        self.setMinimumSize(700, 500)
        self.resize(900, 600)

        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)
        ))), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E2E;
            }
            QTabWidget::pane {
                border: none;
                background-color: #1E1E2E;
            }
            QTabBar::tab {
                background-color: #2A2A3E;
                color: #A0A0B0;
                padding: 10px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #7C3AED;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3A3A50;
            }
        """)

        self._tabs = QTabWidget()
        self._dashboard = DashboardWidget(database, config, tracker, activity, aggregator)
        self._history = HistoryWidget(database, aggregator)
        self._settings = SettingsWidget(config)

        self._tabs.addTab(self._dashboard, "📊 Dashboard")
        self._tabs.addTab(self._history, "📅 Histórico")
        self._tabs.addTab(self._settings, "⚙ Configurações")
        self.setCentralWidget(self._tabs)

        toolbar = QToolBar("Principal")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2A2A3E;
                border: none;
                padding: 4px;
                spacing: 8px;
            }
            QToolButton {
                background-color: transparent;
                color: #E0E0E0;
                border: 1px solid #3A3A50;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: #3A3A50;
            }
        """)

        self._pause_action = QAction("⏸ Pausar", self)
        self._pause_action.triggered.connect(self._toggle_tracking)
        toolbar.addAction(self._pause_action)

        export_action = QAction("📥 Exportar CSV", self)
        export_action.triggered.connect(self._export_today)
        toolbar.addAction(export_action)

        self.addToolBar(toolbar)

        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2A2A3E;
                color: #A0A0B0;
                font-size: 11px;
                padding: 4px 12px;
                border-top: 1px solid #3A3A50;
            }
        """)
        self.setStatusBar(self._status_bar)
        self._update_status()

    def _toggle_tracking(self):
        if self._is_tracking:
            self._tracker.pause()
            self._is_tracking = False
            self._pause_action.setText("▶ Retomar")
        else:
            self._tracker.resume()
            self._is_tracking = True
            self._pause_action.setText("⏸ Pausar")
        self._update_status()

    def update_tracking_state(self, is_tracking):
        self._is_tracking = is_tracking
        if is_tracking:
            self._pause_action.setText("⏸ Pausar")
        else:
            self._pause_action.setText("▶ Retomar")
        self._update_status()

    def _update_status(self):
        try:
            if self._is_tracking:
                state_text = "● Ativo" if self._activity.current_state == "active" else "● Pausa"
                state_color = "#22C55E" if self._activity.current_state == "active" else "#EF4444"
            else:
                state_text = "● Rastreamento pausado"
                state_color = "#F59E0B"

            rate = self._aggregator.get_current_hour_clicks()
            self._status_bar.showMessage(
                f"  {state_text}  |  🖱 {rate} cliques/hora  |  Rastreando..."
                if self._is_tracking else
                f"  {state_text}  |  Rastreamento suspenso"
            )
            self._status_bar.setStyleSheet(f"""
                QStatusBar {{
                    background-color: #2A2A3E;
                    color: {state_color};
                    font-size: 11px;
                    padding: 4px 12px;
                    border-top: 1px solid #3A3A50;
                }}
            """)
        except Exception:
            pass

    def _export_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        default_name = f"clickpulse_{today}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", default_name, "CSV Files (*.csv)"
        )
        if path:
            try:
                self._aggregator.aggregate_hour(
                    datetime.now().replace(minute=0, second=0, microsecond=0)
                )
                Exporter.export_day_csv(self._db, today, path)
                QMessageBox.information(self, "Sucesso", f"Dados exportados para:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")

    def refresh_dashboard(self):
        self._dashboard.refresh()
        self._update_status()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
