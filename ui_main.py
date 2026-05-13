"""Ventana principal con grid 3x2 de las 6 teclas del macropad."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import config
import actions
from ui_editor import KeyEditor

KEY_LAYOUT = [
    ["r", "x", "s"],
    ["f", "j", "num 9"],
]

CARD_QSS = """
QFrame#keyCard {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 12px;
}
QFrame#keyCard:hover {
    border: 1px solid #89b4fa;
    background-color: #232336;
}
QLabel#keyName {
    color: #cdd6f4;
    font-size: 18px;
    font-weight: 600;
}
QLabel#keyHint {
    color: #6c7086;
    font-size: 11px;
}
QLabel#keyAction {
    color: #a6e3a1;
    font-size: 13px;
}
"""

WINDOW_QSS = """
QMainWindow, QWidget#root {
    background-color: #11111b;
}
QLabel#title {
    color: #cdd6f4;
    font-size: 22px;
    font-weight: 700;
}
QLabel#statusActive {
    color: #a6e3a1;
    font-weight: 600;
}
QLabel#statusInactive {
    color: #f38ba8;
    font-weight: 600;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #45475a;
}
QPushButton#primary {
    background-color: #89b4fa;
    color: #11111b;
    font-weight: 600;
}
QPushButton#primary:hover {
    background-color: #a6c5fc;
}
"""


class KeyCard(QFrame):
    clicked = pyqtSignal(str)  # emite el id de la tecla

    def __init__(self, key_id, label, binding):
        super().__init__()
        self.key_id = key_id
        self.setObjectName("keyCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(180, 120)

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(4)

        name_lbl = QLabel(label)
        name_lbl.setObjectName("keyName")

        hint_lbl = QLabel(f"código: {config.KEY_INTERNAL[key_id]}")
        hint_lbl.setObjectName("keyHint")

        self.action_lbl = QLabel(config.describe(binding))
        self.action_lbl.setObjectName("keyAction")
        self.action_lbl.setWordWrap(True)

        v.addWidget(name_lbl)
        v.addWidget(hint_lbl)
        v.addStretch()
        v.addWidget(self.action_lbl)

    def update_binding(self, binding):
        self.action_lbl.setText(config.describe(binding))

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.key_id)


class MainWindow(QMainWindow):
    config_changed = pyqtSignal()
    toggle_enabled = pyqtSignal(bool)

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle("Macropad Shortcuts")
        self.setMinimumSize(720, 480)
        self.setStyleSheet(WINDOW_QSS + CARD_QSS)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(18)

        # header
        header = QHBoxLayout()
        title = QLabel("Macropad Shortcuts")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        self.status_lbl = QLabel()
        self._refresh_status()
        header.addWidget(self.status_lbl)
        outer.addLayout(header)

        subtitle = QLabel(
            "Haz clic en una tecla para asignarle un combo, una app, una URL, "
            "un comando o un texto."
        )
        subtitle.setStyleSheet("color: #6c7086; font-size: 12px;")
        outer.addWidget(subtitle)

        # grid
        grid = QGridLayout()
        grid.setSpacing(14)
        self.cards = {}
        for r, row in enumerate(KEY_LAYOUT):
            for c, key_id in enumerate(row):
                card = KeyCard(
                    key_id,
                    config.KEY_LABELS[key_id],
                    self.cfg["bindings"][key_id],
                )
                card.clicked.connect(self._edit_key)
                self.cards[key_id] = card
                grid.addWidget(card, r, c)
        outer.addLayout(grid)

        # footer
        footer = QHBoxLayout()
        self.toggle_btn = QPushButton()
        self._refresh_toggle_btn()
        self.toggle_btn.clicked.connect(self._toggle)
        footer.addWidget(self.toggle_btn)
        footer.addStretch()

        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save)
        footer.addWidget(save_btn)
        outer.addLayout(footer)

    # ---- handlers ----
    def _edit_key(self, key_id):
        binding = self.cfg["bindings"][key_id]
        dlg = KeyEditor(config.KEY_LABELS[key_id], binding, self)
        if dlg.exec():
            new = dlg.result_binding()
            self.cfg["bindings"][key_id] = new
            self.cards[key_id].update_binding(new)

    def _toggle(self):
        self.cfg["enabled"] = not self.cfg.get("enabled", True)
        self._refresh_status()
        self._refresh_toggle_btn()
        self.toggle_enabled.emit(self.cfg["enabled"])

    def _refresh_status(self):
        if self.cfg.get("enabled", True):
            self.status_lbl.setText("● Activo")
            self.status_lbl.setObjectName("statusActive")
        else:
            self.status_lbl.setText("● Pausado")
            self.status_lbl.setObjectName("statusInactive")
        # forzar redraw del estilo
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)

    def _refresh_toggle_btn(self):
        self.toggle_btn.setText(
            "Pausar shortcuts" if self.cfg.get("enabled", True) else "Activar shortcuts"
        )

    def _save(self):
        try:
            config.save(self.cfg)
            self.config_changed.emit()
            QMessageBox.information(self, "Guardado", "Configuración guardada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def closeEvent(self, ev):
        # Solo ocultar — la app sigue viva en el tray.
        ev.ignore()
        self.hide()
