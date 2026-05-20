# Instalar macropad-shortcuts con Claude Code

Pega este archivo entero en Claude Code. El agente se encarga de todo: clona el repo, instala dependencias, escribe la configuración, opcionalmente registra autostart al login y arranca la app.

---

## 👋 Para el agente (Claude Code)

Eres un agente de instalación. Tu trabajo:

1. Verificar que estás en **Windows** con **Python 3.10+** y `git` disponibles. Si falta algo, **detente y avísale al usuario** — no intentes instalar Python.
2. Clonar el repo si no está ya en disco.
3. Instalar dependencias de Python.
4. Leer la sección **"🎛️ Bindings deseados"** de este archivo y traducirla a `config.json`.
5. Escribir `config.json` en `%LOCALAPPDATA%\MacropadShortcuts\config.json` (crea la carpeta si no existe).
6. Preguntarle al usuario si quiere **autostart al login** de Windows. Si responde sí, registra la entrada en `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
7. Lanzar la app en background (`Start-Process python -ArgumentList "app.py" -WorkingDirectory "<repo>"`).
8. Reportar PID + ubicación del config + estado del autostart.

Antes de escribir el config, **muéstrale al usuario el mapeo que entendiste** (tecla → acción) y pídele confirmación. No asumas — pregunta si algo de la sección de bindings está ambiguo (ej. ruta de un .exe que no existe, URL incompleta).

Si la sección de bindings está vacía o tiene placeholders sin reemplazar (`<...>`), **detente** y pídele al usuario que la complete primero.

---

## 📋 Pasos detallados

### 1. Pre-flight

```powershell
python --version    # debe ser 3.10 o superior
git --version
```

### 2. Clonar (skip si ya está)

```powershell
$repo = "$env:USERPROFILE\Desktop\macropad-shortcuts"
if (-not (Test-Path $repo)) {
  git clone https://github.com/Oruga420/macropad-shortcuts.git $repo
}
```

### 3. Dependencias

```powershell
pip install PyQt6 keyboard
```

`keyboard` necesita permisos administrativos para hookear el teclado a bajo nivel. Si el usuario no corre como admin, avísale — la app cargará pero no captará pulsaciones.

### 4. Generar `config.json`

Carpeta destino: `$env:LOCALAPPDATA\MacropadShortcuts\config.json`.

**Esquema** (ver fuente en [`config.py`](config.py)):

```jsonc
{
  "enabled": true,
  "bindings": {
    "r":     { "type": "...", "value": "..." },
    "x":     { "type": "...", "value": "..." },
    "s":     { "type": "...", "value": "..." },
    "f":     { "type": "...", "value": "..." },
    "j":     { "type": "...", "value": "..." },
    "num 9": { "type": "...", "value": "..." }
  }
}
```

**Tipos válidos de `type`:**

| `type`    | `value`                                | Notas                                                          |
|-----------|----------------------------------------|----------------------------------------------------------------|
| `combo`   | `"ctrl+shift+t"`, `"shift+tab"`, `"f5"`| Formato del paquete `keyboard` (todo lowercase, `+` separador).|
| `app`     | `"C:\\Path\\To\\App.exe"`              | Ruta absoluta. Doble backslash en JSON.                        |
| `url`     | `"https://example.com"`                | Se abre en el navegador por defecto.                           |
| `command` | `"explorer C:\\Users"`                 | Acepta `"terminal": true` para abrir en PowerShell.            |
| `text`    | `"texto literal\nmulti-línea"`         | El texto se escribe tal cual.                                  |
| `none`    | `""`                                   | Tecla sin asignar.                                             |

**IDs de tecla válidos** (los únicos seis aceptados): `r`, `x`, `s`, `f`, `j`, `num 9` (con espacio, lowercase). No agregues otras claves al objeto `bindings`.

### 5. Autostart al login (opcional)

Pregunta primero. Si el usuario dice sí:

```powershell
$cmd = "`"$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe`" `"$env:USERPROFILE\Desktop\macropad-shortcuts\app.py`""
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "MacropadShortcuts" -Value $cmd
```

Notas:
- Usa **`pythonw.exe`** (no `python.exe`) para que no aparezca consola.
- La ruta exacta de `pythonw.exe` puede variar — verifica con `(Get-Command pythonw).Source`.
- Para deshacer: `Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "MacropadShortcuts"`.

### 6. Arrancar la app

```powershell
Start-Process python -ArgumentList "app.py" -WorkingDirectory "$env:USERPROFILE\Desktop\macropad-shortcuts"
```

Verifica que el proceso esté vivo:

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*app.py*' } | Select-Object ProcessId
```

---

## 🎛️ Bindings deseados

> **Usuario:** edita esta sección antes de pasársela al agente. Describe en lenguaje natural qué quieres en cada tecla. Si dejas alguna en blanco o con `<...>`, el agente se detendrá y te lo pedirá.

- **Tecla 1 (R)**: `<describe qué quieres aquí — ej. "abre Spotify"; "combo ctrl+shift+t"; "escribe mi email alex@pricepoint.co">`
- **Tecla 2 (X)**: `<...>`
- **Tecla 3 (S)**: `<...>`
- **Tecla 4 (F)**: `<...>`
- **Tecla 5 (J)**: `<...>`
- **Tecla 6 (Num9)**: `<...>`

**Autostart al login:** `<sí | no>`

---

## 🔁 Re-configurar después

Si más adelante quieres cambiar bindings sin volver a pegar este MD:

- Por UI: abre la app (ícono en la tray) → click en una tecla → editor.
- A mano: edita `%LOCALAPPDATA%\MacropadShortcuts\config.json` y reinicia la app.
- Con Claude Code: vuelve a editar la sección de bindings de arriba y pásale solo esa parte + el esquema.

## 🐞 Si algo no captura

- La app está oculta en tray (ícono 6 cuadritos). Asegúrate que el ícono esté **verde**, no gris (pausa).
- `keyboard` requiere admin. Cierra la app y relanza desde PowerShell elevada.
- Verifica que el macropad esté mandando `Alt+R/X/S/F/J/Num9` con timing < 5 ms — usa `python capture_kb.py` (genera un log) para diagnosticar.
