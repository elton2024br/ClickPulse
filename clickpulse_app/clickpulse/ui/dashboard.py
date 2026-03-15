from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
import pyqtgraph as pg


class StatCard(QFrame):
    def __init__(self, icon, title, value="0", color="#7C3AED"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2A2A3E;
                border-radius: 12px;
                padding: 16px;
                border: 1px solid #3A3A50;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(icon_label)

        self._value_label = QLabel(value)
        self._value_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self._value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self._value_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet("color: #A0A0B0;")
        layout.addWidget(title_label)

    def set_value(self, value):
        self._value_label.setText(str(value))


class PieChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 200)
        self._data = {"left": 0, "right": 0, "middle": 0}
        self._colors = {
            "left": QColor("#3B82F6"),
            "right": QColor("#22C55E"),
            "middle": QColor("#F59E0B"),
        }
        self._labels = {
            "left": "Esquerdo",
            "right": "Direito",
            "middle": "Meio",
        }

    def set_data(self, left, right, middle):
        self._data = {"left": left, "right": right, "middle": middle}
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        total = sum(self._data.values())
        if total == 0:
            painter.setPen(QColor("#A0A0B0"))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Sem dados")
            painter.end()
            return

        w = self.width()
        h = self.height()
        size = min(w, h - 60) - 20
        x = (w - size) // 2
        y = 10
        rect = QRectF(x, y, size, size)

        start_angle = 90 * 16
        for key in ["left", "right", "middle"]:
            value = self._data[key]
            if value == 0:
                continue
            span = int((value / total) * 360 * 16)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self._colors[key]))
            painter.drawPie(rect, start_angle, span)
            start_angle += span

        legend_y = y + size + 15
        painter.setFont(QFont("Segoe UI", 10))
        legend_x = 10
        for key in ["left", "right", "middle"]:
            value = self._data[key]
            pct = (value / total * 100) if total > 0 else 0
            painter.setBrush(QBrush(self._colors[key]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(legend_x, legend_y, 10, 10)
            painter.setPen(QColor("#E0E0E0"))
            text = f"{self._labels[key]}: {pct:.0f}%"
            painter.drawText(legend_x + 14, legend_y + 10, text)
            legend_x += 100

        painter.end()


class ActivityTimeline(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(50)
        self.setMaximumHeight(60)
        self._periods = []

    def set_periods(self, periods):
        self._periods = periods
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width() - 20
        h = 30
        x_off = 10
        y_off = 5

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#2A2A3E")))
        painter.drawRoundedRect(x_off, y_off, w, h, 6, 6)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        day_seconds = 86400

        for p in self._periods:
            try:
                start = datetime.strptime(p["start_time"], "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                continue
            if p["end_time"]:
                try:
                    end = datetime.strptime(p["end_time"], "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    end = datetime.now()
            else:
                end = datetime.now()

            start_sec = max(0, (start - today).total_seconds())
            end_sec = min(day_seconds, (end - today).total_seconds())

            if end_sec <= start_sec:
                continue

            px_start = x_off + int((start_sec / day_seconds) * w)
            px_end = x_off + int((end_sec / day_seconds) * w)
            px_width = max(1, px_end - px_start)

            color = QColor("#22C55E") if p["type"] == "active" else QColor("#EF4444")
            painter.setBrush(QBrush(color))
            painter.drawRect(px_start, y_off, px_width, h)

        now_sec = (datetime.now() - today).total_seconds()
        now_px = x_off + int((now_sec / day_seconds) * w)
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.drawLine(now_px, y_off - 2, now_px, y_off + h + 2)

        painter.setPen(QColor("#A0A0B0"))
        painter.setFont(QFont("Segoe UI", 9))
        for hour in [0, 6, 12, 18, 24]:
            hx = x_off + int((hour / 24) * w)
            painter.drawText(hx - 10, y_off + h + 15, f"{hour}h")

        painter.end()


class DashboardWidget(QWidget):
    def __init__(self, database, config, tracker, activity, aggregator):
        super().__init__()
        self._db = database
        self._config = config
        self._tracker = tracker
        self._activity = activity
        self._aggregator = aggregator
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)
        self._card_clicks = StatCard("🖱", "Cliques hoje", "0", "#7C3AED")
        self._card_active = StatCard("⏱", "Tempo ativo", "0h 0m", "#22C55E")
        self._card_pause = StatCard("⏸", "Pausas", "0h 0m", "#EF4444")
        self._card_rate = StatCard("📊", "Cliques/hora", "0", "#3B82F6")
        cards_layout.addWidget(self._card_clicks)
        cards_layout.addWidget(self._card_active)
        cards_layout.addWidget(self._card_pause)
        cards_layout.addWidget(self._card_rate)
        layout.addLayout(cards_layout)

        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(12)

        pg.setConfigOptions(background="#1E1E2E", foreground="#E0E0E0")
        self._bar_plot = pg.PlotWidget(title="Cliques por Hora")
        self._bar_plot.setLabel("bottom", "Hora")
        self._bar_plot.setLabel("left", "Cliques")
        self._bar_plot.showGrid(y=True, alpha=0.2)
        self._bar_plot.setMinimumHeight(200)
        charts_layout.addWidget(self._bar_plot, stretch=3)

        pie_container = QVBoxLayout()
        pie_label = QLabel("Tipos de clique")
        pie_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        pie_label.setStyleSheet("color: #E0E0E0;")
        pie_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pie_container.addWidget(pie_label)
        self._pie_chart = PieChartWidget()
        self._pie_chart.setMinimumWidth(200)
        pie_container.addWidget(self._pie_chart)
        pie_wrapper = QWidget()
        pie_wrapper.setLayout(pie_container)
        charts_layout.addWidget(pie_wrapper, stretch=2)
        layout.addLayout(charts_layout)

        timeline_label = QLabel("Timeline de Atividade")
        timeline_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        timeline_label.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(timeline_label)

        self._timeline = ActivityTimeline()
        layout.addWidget(self._timeline)

        layout.addStretch()

    def refresh(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            counts = self._db.count_clicks_in_range(today, tomorrow)

            self._card_clicks.set_value(str(counts["total"]))

            active = self._activity.active_time_today
            ah = int(active.total_seconds()) // 3600
            am = (int(active.total_seconds()) % 3600) // 60
            self._card_active.set_value(f"{ah}h {am}m")

            pause = self._activity.pause_time_today
            ph = int(pause.total_seconds()) // 3600
            pm = (int(pause.total_seconds()) % 3600) // 60
            self._card_pause.set_value(f"{ph}h {pm}m")

            current_rate = self._aggregator.get_current_hour_clicks()
            self._card_rate.set_value(str(current_rate))

            self._pie_chart.set_data(
                counts["left_clicks"],
                counts["right_clicks"],
                counts["middle_clicks"],
            )

            self._update_bar_chart(today)

            periods = self._db.get_activity_periods_in_range(today, tomorrow)
            self._timeline.set_periods(periods)
        except Exception:
            pass

    def _update_bar_chart(self, today):
        self._bar_plot.clear()
        hourly = self._aggregator.get_hourly_stats(today)

        hours_data = {}
        for h in hourly:
            try:
                hour = datetime.strptime(h["hour_start"], "%Y-%m-%d %H:%M:%S").hour
                hours_data[hour] = h["total_clicks"]
            except (ValueError, TypeError):
                pass

        current_hour = datetime.now().hour
        current_clicks = self._aggregator.get_current_hour_clicks()
        hours_data[current_hour] = current_clicks

        if not hours_data:
            return

        x_vals = list(range(24))
        y_vals = [hours_data.get(h, 0) for h in x_vals]
        colors = []
        for h in x_vals:
            if h == current_hour:
                colors.append(QColor("#7C3AED"))
            else:
                colors.append(QColor("#3B82F6"))

        bar = pg.BarGraphItem(x=x_vals, height=y_vals, width=0.6, brushes=colors)
        self._bar_plot.addItem(bar)
        self._bar_plot.setXRange(-0.5, 23.5)
