"""
Captures every key event Windows sees from any keyboard.
Press the 6 macropad keys (and optionally use the knob) one at a time.
Output goes to capture_kb.log.
NOTE: must run as the same user that has focus. Run normally, no admin needed
on most setups (admin only required to capture inside elevated windows).
"""
import keyboard
import time
import sys

LOG_PATH = r"C:\Users\user\Desktop\macropad-shortcuts\capture_kb.log"

t0 = time.time()
log = open(LOG_PATH, "w", buffering=1, encoding="utf-8")

def emit(line):
    print(line, flush=True)
    log.write(line + "\n")
    log.flush()

def on_event(e):
    ts = time.time() - t0
    # event has: event_type ('down'/'up'), name, scan_code, time, is_keypad, modifiers
    emit(
        f"[{ts:7.3f}s] {e.event_type:4s}  "
        f"name={e.name!r:20s} scan_code={e.scan_code:#06x}  "
        f"is_keypad={e.is_keypad}"
    )

emit("=" * 70)
emit("Listening for ALL key events. Press macropad keys.")
emit("Press ESC twice in a row (within 1 second) to stop.")
emit("=" * 70)

keyboard.hook(on_event)

last_esc = 0
def esc_watch(e):
    global last_esc
    if e.name == "esc" and e.event_type == "down":
        now = time.time()
        if now - last_esc < 1.0:
            emit("Stopping...")
            log.close()
            sys.exit(0)
        last_esc = now

keyboard.hook(esc_watch)

# block forever; the keyboard library runs its own listener thread.
keyboard.wait()
