"""Carga y guarda la configuración de los bindings."""
import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.environ["LOCALAPPDATA"]) / "MacropadShortcuts"
CONFIG_PATH = CONFIG_DIR / "config.json"

KEYS = ["r", "x", "s", "f", "j", "num 9"]
# Etiquetas que ve el usuario (numeración 1..6 en orden de grid).
KEY_LABELS = {
    "r": "Tecla 1",
    "x": "Tecla 2",
    "s": "Tecla 3",
    "f": "Tecla 4",
    "j": "Tecla 5",
    "num 9": "Tecla 6",
}
# Código interno (lo que envía el hardware) — solo para debug.
KEY_INTERNAL = {
    "r": "Alt+R",
    "x": "Alt+X",
    "s": "Alt+S",
    "f": "Alt+F",
    "j": "Alt+J",
    "num 9": "Alt+Num9",
}

DEFAULT_BINDING = {"type": "none", "value": ""}

def default_config():
    return {
        "enabled": True,
        "bindings": {k: dict(DEFAULT_BINDING) for k in KEYS},
    }

def load():
    if not CONFIG_PATH.exists():
        return default_config()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return default_config()

    cfg = default_config()
    cfg["enabled"] = bool(data.get("enabled", True))
    saved_bindings = data.get("bindings", {})
    for k in KEYS:
        b = saved_bindings.get(k)
        if isinstance(b, dict) and "type" in b and "value" in b:
            entry = {"type": b["type"], "value": b["value"]}
            if b.get("terminal"):
                entry["terminal"] = True
            cfg["bindings"][k] = entry
    return cfg

def save(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def describe(binding):
    """Devuelve un texto corto en español para mostrar en la UI."""
    t = binding.get("type", "none")
    v = binding.get("value", "")
    if t == "none" or not v:
        return "Sin asignar"
    if t == "combo":
        return f"⌨ {v}"
    if t == "app":
        name = Path(v).name
        return f"▶ {name}"
    if t == "url":
        return f"🌐 {v}"
    if t == "command":
        prefix = "$" if not binding.get("terminal") else "▣"
        return f"{prefix} {v[:30]}{'…' if len(v) > 30 else ''}"
    if t == "text":
        preview = v.replace("\n", " ")[:25]
        return f"✎ {preview}{'…' if len(v) > 25 else ''}"
    return v
