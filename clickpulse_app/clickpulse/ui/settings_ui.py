from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QGroupBox, QFormLayout, QMessageBox,
)
from PyQt6.QtGui import QFont

from clickpulse.config import DEFAULTS


class SettingsWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self._config = config
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Configurações")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(title)

        group = QGroupBox("Parâmetros de Rastreamento")
        group.setStyleSheet("""
            QGroupBox {
                color: #E0E0E0;
                border: 1px solid #3A3A50;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 8px;
            }
        """)
        form = QFormLayout(group)
        form.setSpacing(12)

        spinbox_style = """
            QSpinBox {
                background-color: #2A2A3E;
                color: #E0E0E0;
                border: 1px solid #3A3A50;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 120px;
            }
        """

        label_style = "color: #E0E0E0; font-size: 12px;"

        self._pause_threshold = QSpinBox()
        self._pause_threshold.setRange(1, 30)
        self._pause_threshold.setValue(self._config.pause_threshold_minutes)
        self._pause_threshold.setSuffix(" min")
        self._pause_threshold.setStyleSheet(spinbox_style)
        lbl = QLabel("Threshold de pausa:")
        lbl.setStyleSheet(label_style)
        form.addRow(lbl, self._pause_threshold)

        self._long_pause = QSpinBox()
        self._long_pause.setRange(10, 120)
        self._long_pause.setValue(self._config.long_pause_alert_minutes)
        self._long_pause.setSuffix(" min")
        self._long_pause.setStyleSheet(spinbox_style)
        lbl2 = QLabel("Alerta de pausa longa:")
        lbl2.setStyleSheet(label_style)
        form.addRow(lbl2, self._long_pause)

        self._milestone = QSpinBox()
        self._milestone.setRange(50, 1000)
        self._milestone.setSingleStep(50)
        self._milestone.setValue(self._config.notification_click_milestone)
        self._milestone.setSuffix(" cliques")
        self._milestone.setStyleSheet(spinbox_style)
        lbl3 = QLabel("Milestone de cliques:")
        lbl3.setStyleSheet(label_style)
        form.addRow(lbl3, self._milestone)

        self._check_interval = QSpinBox()
        self._check_interval.setRange(1, 60)
        self._check_interval.setValue(self._config.activity_check_seconds)
        self._check_interval.setSuffix(" seg")
        self._check_interval.setStyleSheet(spinbox_style)
        lbl4 = QLabel("Intervalo de verificação:")
        lbl4.setStyleSheet(label_style)
        form.addRow(lbl4, self._check_interval)

        layout.addWidget(group)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        save_btn = QPushButton("💾 Salvar")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
        """)
        save_btn.clicked.connect(self._save)
        buttons.addWidget(save_btn)

        reset_btn = QPushButton("🔄 Restaurar padrões")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        reset_btn.clicked.connect(self._reset)
        buttons.addWidget(reset_btn)

        buttons.addStretch()
        layout.addLayout(buttons)
        layout.addStretch()

    def _save(self):
        self._config.set("pause_threshold_minutes", self._pause_threshold.value())
        self._config.set("long_pause_alert_minutes", self._long_pause.value())
        self._config.set("notification_click_milestone", self._milestone.value())
        self._config.set("activity_check_seconds", self._check_interval.value())
        QMessageBox.information(self, "Salvo", "Configurações salvas com sucesso!")

    def _reset(self):
        self._config.reset_defaults()
        self._pause_threshold.setValue(DEFAULTS["pause_threshold_minutes"])
        self._long_pause.setValue(DEFAULTS["long_pause_alert_minutes"])
        self._milestone.setValue(DEFAULTS["notification_click_milestone"])
        self._check_interval.setValue(DEFAULTS["activity_check_seconds"])
        QMessageBox.information(self, "Restaurado", "Configurações restauradas para padrão!")
