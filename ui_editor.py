"""Diálogo de edición de un binding."""
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

QT_MOD_NAMES = [
    (Qt.KeyboardModifier.ControlModifier, "ctrl"),
    (Qt.KeyboardModifier.AltModifier, "alt"),
    (Qt.KeyboardModifier.ShiftModifier, "shift"),
    (Qt.KeyboardModifier.MetaModifier, "windows"),
]

class ComboCapture(QLineEdit):
    """QLineEdit que captura combos de teclado en vez de texto."""
    def __init__(self, initial=""):
        super().__init__()
        self.setPlaceholderText("Haz clic aquí y presiona la combinación…")
        self.setReadOnly(True)
        self.setText(initial)

    def focusNextPrevChild(self, next):
        # Evita que Tab / Shift+Tab muevan el foco fuera del capturador.
        return False

    def keyPressEvent(self, ev):
        key = ev.key()
        if key in (
            Qt.Key.Key_Control, Qt.Key.Key_Alt,
            Qt.Key.Key_Shift, Qt.Key.Key_Meta,
        ):
            return  # modificador solo, esperamos la tecla principal
        if key == Qt.Key.Key_Escape:
            self.setText("")
            return
        parts = []
        mods = ev.modifiers()
        for flag, name in QT_MOD_NAMES:
            if mods & flag:
                parts.append(name)
        # Qt manda Key_Backtab cuando hay Shift+Tab; QKeySequence lo
        # serializa como "backtab", que el lib `keyboard` no reconoce.
        if key in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
            key_text = "tab"
            if key == Qt.Key.Key_Backtab and "shift" not in parts:
                parts.append("shift")
        else:
            key_text = QKeySequence(key).toString().lower()
        if key_text:
            parts.append(key_text)
        if parts:
            self.setText("+".join(parts))


class KeyEditor(QDialog):
    def __init__(self, key_label, binding, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Editar {key_label}")
        self.setMinimumWidth(460)
        self._binding = dict(binding)

        v = QVBoxLayout(self)
        title = QLabel(f"<h3>{key_label}</h3>")
        v.addWidget(title)

        self.tabs = QTabWidget()
        v.addWidget(self.tabs)

        self.tabs.addTab(self._tab_combo(), "Combo")
        self.tabs.addTab(self._tab_app(), "App / Archivo")
        self.tabs.addTab(self._tab_url(), "URL")
        self.tabs.addTab(self._tab_command(), "Comando")
        self.tabs.addTab(self._tab_text(), "Texto")
        self.tabs.addTab(self._tab_none(), "Sin asignar")

        # Selecciona tab según binding actual
        type_to_idx = {"combo": 0, "app": 1, "url": 2, "command": 3, "text": 4, "none": 5}
        self.tabs.setCurrentIndex(type_to_idx.get(binding.get("type", "none"), 5))

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Guardar")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        v.addWidget(btns)

    # ---- tabs ----
    def _tab_combo(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel(
            "Presiona el combo que quieres que la tecla envíe.\n"
            "Ejemplo: Ctrl+Shift+T, Ctrl+C, F5."
        ))
        initial = self._binding.get("value", "") if self._binding.get("type") == "combo" else ""
        self.combo_input = ComboCapture(initial)
        lay.addWidget(self.combo_input)

        clear = QPushButton("Limpiar")
        clear.clicked.connect(lambda: self.combo_input.setText(""))
        lay.addWidget(clear)
        lay.addStretch()
        return w

    def _tab_app(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel("Ruta a la aplicación o archivo a abrir:"))
        h = QHBoxLayout()
        self.app_input = QLineEdit()
        if self._binding.get("type") == "app":
            self.app_input.setText(self._binding.get("value", ""))
        h.addWidget(self.app_input)
        browse = QPushButton("Examinar…")
        browse.clicked.connect(self._browse_app)
        h.addWidget(browse)
        lay.addLayout(h)
        lay.addWidget(QLabel(
            "<i>Tip: también puedes pegar la ruta directamente.</i>"
        ))
        lay.addStretch()
        return w

    def _browse_app(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona aplicación o archivo",
            "",
            "Ejecutables (*.exe);;Todos los archivos (*.*)"
        )
        if path:
            self.app_input.setText(path)

    def _tab_url(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel("URL a abrir en el navegador:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://…")
        if self._binding.get("type") == "url":
            self.url_input.setText(self._binding.get("value", ""))
        lay.addWidget(self.url_input)
        lay.addStretch()
        return w

    def _tab_command(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel(
            "Comando a ejecutar.\n"
            "Ejemplo: explorer C:\\, code, dir"
        ))
        self.cmd_input = QLineEdit()
        if self._binding.get("type") == "command":
            self.cmd_input.setText(self._binding.get("value", ""))
        lay.addWidget(self.cmd_input)

        self.cmd_terminal = QCheckBox(
            "Abrir en una ventana de PowerShell\n"
            "(necesario para herramientas interactivas como Claude Code, ssh, REPLs)"
        )
        if self._binding.get("type") == "command" and self._binding.get("terminal"):
            self.cmd_terminal.setChecked(True)
        lay.addWidget(self.cmd_terminal)

        lay.addStretch()
        return w

    def _tab_text(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel("Texto que la tecla escribirá:"))
        self.text_input = QPlainTextEdit()
        if self._binding.get("type") == "text":
            self.text_input.setPlainText(self._binding.get("value", ""))
        lay.addWidget(self.text_input)
        return w

    def _tab_none(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel(
            "La tecla no hará nada cuando se presione.\n"
            "Selecciona esta opción si quieres dejarla libre."
        ))
        lay.addStretch()
        return w

    # ---- result ----
    def result_binding(self):
        idx = self.tabs.currentIndex()
        if idx == 0:
            return {"type": "combo", "value": self.combo_input.text().strip()}
        if idx == 1:
            return {"type": "app", "value": self.app_input.text().strip()}
        if idx == 2:
            return {"type": "url", "value": self.url_input.text().strip()}
        if idx == 3:
            return {
                "type": "command",
                "value": self.cmd_input.text().strip(),
                "terminal": self.cmd_terminal.isChecked(),
            }
        if idx == 4:
            return {"type": "text", "value": self.text_input.toPlainText()}
        return {"type": "none", "value": ""}
