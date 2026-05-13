"""Entry point. Tray + ventana + listener."""
import sys
import threading

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPainter, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

import config
from listener import Listener
from ui_main import MainWindow


def make_icon(active=True):
    """Genera un ícono 64x64 sencillo: 6 cuadritos en grid 3x2."""
    pm = QPixmap(64, 64)
    pm.fill(QColor("#11111b"))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    color = QColor("#a6e3a1") if active else QColor("#6c7086")
    p.setBrush(color)
    p.setPen(QColor("#11111b"))
    cell_w, cell_h = 16, 22
    margin_x = (64 - cell_w * 3 - 4) // 2
    margin_y = (64 - cell_h * 2 - 4) // 2
    for r in range(2):
        for c in range(3):
            x = margin_x + c * (cell_w + 2)
            y = margin_y + r * (cell_h + 2)
            p.drawRoundedRect(x, y, cell_w, cell_h, 3, 3)
    p.end()
    return QIcon(pm)


class AppController(QObject):
    def __init__(self):
        super().__init__()
        self.cfg = config.load()
        self.window = MainWindow(self.cfg)
        self.window.toggle_enabled.connect(self._on_toggle)
        self.window.config_changed.connect(lambda: None)  # cfg ya es por referencia

        # listener
        self.listener = Listener(get_config=lambda: self.cfg)
        self._start_listener()

        # tray
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(make_icon(self.cfg.get("enabled", True)))
        self.tray.setToolTip("Macropad Shortcuts")
        self._build_tray_menu()
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _start_listener(self):
        # keyboard hooks deben correr en hilo secundario para no bloquear Qt
        def runner():
            try:
                self.listener.start()
            except Exception as e:
                print(f"listener error: {e}")
        t = threading.Thread(target=runner, daemon=True)
        t.start()

    def _build_tray_menu(self):
        menu = QMenu()
        self.act_toggle = QAction()
        self._refresh_toggle_action()
        self.act_toggle.triggered.connect(self._toggle_from_tray)
        menu.addAction(self.act_toggle)
        menu.addSeparator()
        act_open = QAction("Abrir configuración")
        act_open.triggered.connect(self._show_window)
        menu.addAction(act_open)
        menu.addSeparator()
        act_quit = QAction("Salir")
        act_quit.triggered.connect(self._quit)
        menu.addAction(act_quit)
        self.tray.setContextMenu(menu)

    def _refresh_toggle_action(self):
        self.act_toggle.setText(
            "Pausar shortcuts" if self.cfg.get("enabled", True) else "Activar shortcuts"
        )

    def _toggle_from_tray(self):
        self.cfg["enabled"] = not self.cfg.get("enabled", True)
        self._refresh_toggle_action()
        self.tray.setIcon(make_icon(self.cfg["enabled"]))
        # refresh ventana también
        self.window._refresh_status()
        self.window._refresh_toggle_btn()

    def _on_toggle(self, enabled):
        self._refresh_toggle_action()
        self.tray.setIcon(make_icon(enabled))

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self):
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _quit(self):
        try:
            self.listener.stop()
        except Exception:
            pass
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Macropad Shortcuts")

    if not QSystemTrayIcon.isSystemTrayAvailable():
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Macropad Shortcuts",
                             "El system tray no está disponible.")
        sys.exit(1)

    ctl = AppController()
    ctl._show_window()  # arranca con la ventana visible
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
