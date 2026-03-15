from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QFileDialog, QMessageBox,
    QSplitter,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
import pyqtgraph as pg

from clickpulse.exporter import Exporter


class HistoryWidget(QWidget):
    def __init__(self, database, aggregator):
        super().__init__()
        self._db = database
        self._aggregator = aggregator
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        controls = QHBoxLayout()
        controls.setSpacing(12)

        date_label = QLabel("Data:")
        date_label.setFont(QFont("Segoe UI", 11))
        date_label.setStyleSheet("color: #E0E0E0;")
        controls.addWidget(date_label)

        self._date_edit = QDateEdit()
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("dd/MM/yyyy")
        self._date_edit.setStyleSheet("""
            QDateEdit {
                background-color: #2A2A3E;
                color: #E0E0E0;
                border: 1px solid #3A3A50;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QCalendarWidget {
                background-color: #1E1E2E;
                color: #E0E0E0;
            }
            QCalendarWidget QToolButton {
                background-color: #2A2A3E;
                color: #E0E0E0;
                border: 1px solid #3A3A50;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #3A3A50;
            }
            QCalendarWidget QMenu {
                background-color: #2A2A3E;
                color: #E0E0E0;
                border: 1px solid #3A3A50;
            }
            QCalendarWidget QSpinBox {
                background-color: #2A2A3E;
                color: #E0E0E0;
                border: 1px solid #3A3A50;
                border-radius: 4px;
                padding: 2px;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #1E1E2E;
                color: #E0E0E0;
                selection-background-color: #7C3AED;
                selection-color: white;
                alternate-background-color: #252538;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2A2A3E;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #E0E0E0;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #555555;
            }
        """)
        self._date_edit.dateChanged.connect(self._load_data)
        controls.addWidget(self._date_edit)

        range_label = QLabel("Periodo:")
        range_label.setFont(QFont("Segoe UI", 11))
        range_label.setStyleSheet("color: #E0E0E0;")
        controls.addWidget(range_label)

        self._range_combo = QComboBox()
        self._range_combo.addItems(["Dia", "Semana", "Mes"])
        self._range_combo.setStyleSheet("""
            QComboBox {
                background-color: #2A2A3E;
                color: #E0E0E0;
                border: 1px solid #3A3A50;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A3E;
                color: #E0E0E0;
                selection-background-color: #7C3AED;
            }
        """)
        self._range_combo.currentTextChanged.connect(self._load_data)
        controls.addWidget(self._range_combo)

        controls.addStretch()

        export_btn = QPushButton("Exportar CSV")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #7C3AED;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6D28D9;
            }
        """)
        export_btn.clicked.connect(self._export_csv)
        controls.addWidget(export_btn)

        layout.addLayout(controls)

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            "Hora", "Total", "Esquerdo", "Direito",
            "Meio", "Ativo (min)", "Pausa (min)"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E2E;
                color: #E0E0E0;
                border: 1px solid #3A3A50;
                border-radius: 8px;
                gridline-color: #3A3A50;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:alternate {
                background-color: #252538;
            }
            QHeaderView::section {
                background-color: #2A2A3E;
                color: #E0E0E0;
                padding: 8px;
                border: 1px solid #3A3A50;
                font-weight: bold;
            }
        """)
        layout.addWidget(self._table)

        chart_label = QLabel("Comparativo por dia")
        chart_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        chart_label.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(chart_label)

        pg.setConfigOptions(background="#1E1E2E", foreground="#E0E0E0")
        self._compare_chart = pg.PlotWidget()
        self._compare_chart.setLabel("bottom", "Dia")
        self._compare_chart.setLabel("left", "Total de cliques")
        self._compare_chart.showGrid(y=True, alpha=0.2)
        self._compare_chart.setMinimumHeight(160)
        self._compare_chart.setMaximumHeight(200)
        layout.addWidget(self._compare_chart)

        self._summary_label = QLabel("")
        self._summary_label.setFont(QFont("Segoe UI", 11))
        self._summary_label.setStyleSheet("color: #A0A0B0;")
        layout.addWidget(self._summary_label)

    def _get_date_range(self):
        selected = self._date_edit.date().toPyDate()
        range_type = self._range_combo.currentText()

        if range_type == "Dia":
            start = selected
            end = selected + timedelta(days=1)
        elif range_type == "Semana":
            start = selected - timedelta(days=selected.weekday())
            end = start + timedelta(days=7)
        else:
            start = selected.replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)

        return start, end

    def _load_data(self):
        start, end = self._get_date_range()

        all_stats = []
        daily_totals = {}
        current = start
        while current < end:
            day_str = current.strftime("%Y-%m-%d")
            stats = self._aggregator.get_hourly_stats(day_str)
            all_stats.extend(stats)
            day_total = sum(s["total_clicks"] for s in stats)
            daily_totals[day_str] = day_total
            current += timedelta(days=1)

        self._table.setRowCount(len(all_stats))
        total_clicks = 0
        total_active = 0
        total_pause = 0

        for row, stat in enumerate(all_stats):
            try:
                hour_dt = datetime.strptime(stat["hour_start"], "%Y-%m-%d %H:%M:%S")
                hour_str = hour_dt.strftime("%d/%m %Hh")
            except (ValueError, TypeError):
                hour_str = str(stat["hour_start"])

            items = [
                hour_str,
                str(stat["total_clicks"]),
                str(stat["left_clicks"]),
                str(stat["right_clicks"]),
                str(stat["middle_clicks"]),
                str(stat["active_seconds"] // 60),
                str(stat["pause_seconds"] // 60),
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row, col, item)

            total_clicks += stat["total_clicks"]
            total_active += stat["active_seconds"]
            total_pause += stat["pause_seconds"]

        active_h = total_active // 3600
        active_m = (total_active % 3600) // 60
        pause_h = total_pause // 3600
        pause_m = (total_pause % 3600) // 60
        self._summary_label.setText(
            f"Total: {total_clicks} cliques | "
            f"Ativo: {active_h}h {active_m}m | "
            f"Pausa: {pause_h}h {pause_m}m"
        )

        self._update_compare_chart(daily_totals)

    def _update_compare_chart(self, daily_totals):
        self._compare_chart.clear()
        if not daily_totals:
            return

        days = sorted(daily_totals.keys())
        x_vals = list(range(len(days)))
        y_vals = [daily_totals[d] for d in days]

        bar = pg.BarGraphItem(
            x=x_vals, height=y_vals, width=0.6,
            brush=QColor("#7C3AED"),
        )
        self._compare_chart.addItem(bar)

        ticks = [(i, datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m")) for i, d in enumerate(days)]
        ax = self._compare_chart.getAxis("bottom")
        ax.setTicks([ticks])

    def _export_csv(self):
        start, end = self._get_date_range()

        try:
            self._aggregator.aggregate_hour(
                datetime.now().replace(minute=0, second=0, microsecond=0)
            )
        except Exception:
            pass

        default_name = f"clickpulse_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", default_name, "CSV Files (*.csv)"
        )
        if path:
            try:
                start_str = start.strftime("%Y-%m-%d")
                end_str = end.strftime("%Y-%m-%d")
                Exporter.export_range_csv(self._db, start_str, end_str, path)
                QMessageBox.information(self, "Sucesso", f"Dados exportados para:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")
