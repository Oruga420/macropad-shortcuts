"""Ejecutores de las acciones asignadas a las teclas."""
import os
import subprocess
import threading
import time
import webbrowser

import keyboard

def run(binding):
    """Ejecuta una acción. Se llama desde el thread del listener.
    Cualquier acción que pueda bloquear corre en su propio thread.
    """
    t = binding.get("type", "none")
    v = binding.get("value", "")
    if t == "none" or not v:
        return

    if t == "combo":
        _run_combo(v)
    elif t == "app":
        threading.Thread(target=_run_app, args=(v,), daemon=True).start()
    elif t == "url":
        threading.Thread(target=_run_url, args=(v,), daemon=True).start()
    elif t == "command":
        in_terminal = bool(binding.get("terminal"))
        threading.Thread(target=_run_command, args=(v, in_terminal), daemon=True).start()
    elif t == "text":
        threading.Thread(target=_run_text, args=(v,), daemon=True).start()

def _run_combo(combo):
    # pequeño delay para que el alt-up del macropad procese antes de mandar nuevas teclas
    time.sleep(0.02)
    try:
        keyboard.send(combo)
    except Exception as e:
        print(f"combo error: {e}")

def _run_app(path):
    try:
        os.startfile(path)
    except Exception as e:
        print(f"app error: {e}")

def _run_url(url):
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"url error: {e}")

CREATE_NEW_CONSOLE = 0x00000010

def _run_command(cmd, in_terminal=False):
    try:
        if in_terminal:
            # Intenta Windows Terminal primero (mejor UX); si no está, PowerShell.
            wt = _which("wt.exe")
            if wt:
                # wt.exe pwsh -NoExit -Command "<cmd>"
                pwsh = _which("pwsh.exe") or "powershell.exe"
                subprocess.Popen(
                    [wt, pwsh, "-NoExit", "-Command", cmd],
                    creationflags=CREATE_NEW_CONSOLE,
                )
            else:
                subprocess.Popen(
                    ["powershell.exe", "-NoExit", "-Command", cmd],
                    creationflags=CREATE_NEW_CONSOLE,
                )
        else:
            subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"command error: {e}")

def _which(name):
    import shutil
    return shutil.which(name)

def _run_text(text):
    time.sleep(0.02)
    try:
        keyboard.write(text)
    except Exception as e:
        print(f"text error: {e}")
