"""Hook de teclado con detección por timing.

Si Alt + letra llegan dentro de THRESHOLD_MS ms, asumimos macropad,
ejecutamos la acción asignada y suprimimos la letra.
"""
import time
import threading

import keyboard

import actions

THRESHOLD_S = 0.005  # 5ms

ALT_NAMES = {"alt", "left alt", "right alt"}
TARGET_KEYS = {"r", "x", "s", "f", "j", "num 9"}

class Listener:
    def __init__(self, get_config):
        """get_config: callable que devuelve la config actual cada vez."""
        self._get_config = get_config
        self._alt_down_t = None
        self._suppressed_keys = set()  # teclas cuya liberación debemos suprimir
        self._hook = None
        self._lock = threading.Lock()

    def start(self):
        if self._hook is not None:
            return
        self._hook = keyboard.hook(self._on_event, suppress=True)

    def stop(self):
        if self._hook is None:
            return
        keyboard.unhook(self._hook)
        self._hook = None

    def _on_event(self, e):
        cfg = self._get_config()
        if not cfg.get("enabled", True):
            return True  # pasar todo

        name = e.name.lower() if e.name else ""
        et = e.event_type

        # Track Alt
        if name in ALT_NAMES:
            if et == "down":
                with self._lock:
                    self._alt_down_t = time.perf_counter()
            return True  # alt siempre pasa

        if et == "up":
            with self._lock:
                if name in self._suppressed_keys:
                    self._suppressed_keys.discard(name)
                    return False
            return True

        # et == "down"
        if name in TARGET_KEYS:
            with self._lock:
                t0 = self._alt_down_t
            if t0 is not None and (time.perf_counter() - t0) < THRESHOLD_S:
                # Es macropad: dispara y suprime
                binding = cfg["bindings"].get(name)
                if binding:
                    actions.run(binding)
                with self._lock:
                    self._suppressed_keys.add(name)
                return False

        return True
