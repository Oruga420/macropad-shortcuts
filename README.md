# macropad-shortcuts

App de bandeja de Windows que convierte un macropad de 6 teclas (que envía `Alt+R/X/S/F/J/Num9`) en accesos directos configurables: lanzar apps, abrir URLs, ejecutar comandos, enviar combos de teclado o escribir texto.

## Instalación automatizada con Claude Code

¿No quieres clonar, instalar deps y configurar a mano? Descarga **[CLAUDE_INSTALL.md](CLAUDE_INSTALL.md)**, edita la sección "🎛️ Bindings deseados" con lo que quieras en cada tecla, y pégaselo a Claude Code. Hace todo: clona el repo, instala dependencias, escribe `config.json`, registra autostart al login (opcional) y lanza la app.

Raw URL para curl:

```powershell
iwr -OutFile CLAUDE_INSTALL.md https://raw.githubusercontent.com/Oruga420/macropad-shortcuts/main/CLAUDE_INSTALL.md
```

## Cómo funciona

El macropad manda `Alt + <tecla>` en milisegundos. El listener detecta `Alt + tecla objetivo` con `< 5 ms` de diferencia y asume que viene del hardware, no del usuario. En ese caso suprime la pulsación original y dispara la acción asignada. Si lo presionas tú a mano (delay normal humano), pasa de largo.

## Requisitos

- Windows
- Python 3.12
- `PyQt6`
- `keyboard`

```powershell
pip install PyQt6 keyboard
```

El módulo `keyboard` necesita permisos elevados para hookear el teclado a bajo nivel — corre PowerShell como administrador si no captura nada.

## Uso

```powershell
python app.py
```

Abre la ventana de configuración y deja un ícono en la system tray. Por cada tecla del macropad puedes elegir:

- **Combo** — manda otra combinación de teclas (ej. `ctrl+shift+t`)
- **App / Archivo** — abre un ejecutable o archivo
- **URL** — abre una URL en el navegador
- **Comando** — corre un comando (opcionalmente en una ventana de PowerShell)
- **Texto** — escribe texto literal
- **Sin asignar** — la tecla queda libre

La configuración se guarda en `%LOCALAPPDATA%\MacropadShortcuts\config.json`.

## Archivos

- `app.py` — entry point (tray + ventana + listener en thread).
- `listener.py` — hook global de teclado con detección por timing.
- `actions.py` — ejecutores para cada tipo de acción.
- `ui_main.py` — ventana principal con la grid 3x2.
- `ui_editor.py` — diálogo de edición de un binding.
- `config.py` — carga/guarda config en `%LOCALAPPDATA%`.
- `capture.py`, `capture_kb.py`, `enumerate.py` — utilidades de diagnóstico para inspeccionar lo que manda el macropad.

## Pausar

Click derecho en el ícono de la tray → **Pausar shortcuts**. Mientras está en pausa el listener deja pasar todo sin tocar.
