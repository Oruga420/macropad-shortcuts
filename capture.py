import pywinusb.hid as hid
import time
import sys
import threading

VID = 0x1EA7
PID = 0x0169
LOG_PATH = r"C:\Users\user\Desktop\macropad-shortcuts\capture.log"

t0 = time.time()
lock = threading.Lock()
log = open(LOG_PATH, "w", buffering=1, encoding="utf-8")  # line-buffered

def emit(line):
    with lock:
        print(line)
        log.write(line + "\n")
        log.flush()

def make_handler(label):
    def handler(data):
        ts = time.time() - t0
        hex_bytes = " ".join(f"{b:02X}" for b in data)
        emit(f"[{ts:7.3f}s] {label:30s} : {hex_bytes}")
    return handler

devices = hid.HidDeviceFilter(vendor_id=VID, product_id=PID).get_devices()
opened = []

for i, d in enumerate(devices):
    try:
        d.open()
        label = f"dev{i} up=0x{d.hid_caps.usage_page:04X} u=0x{d.hid_caps.usage:04X}"
        d.set_raw_data_handler(make_handler(label))
        opened.append(d)
        emit(f"opened: {label}")
    except Exception as e:
        emit(f"FAILED to open dev{i}: {e}")

if not opened:
    emit("No interfaces opened. Exiting.")
    sys.exit(1)

emit("=" * 70)
emit("Capturing. Press macropad keys / use the knob.")
emit("=" * 70)

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    emit("Stopping...")
finally:
    for d in opened:
        try:
            d.close()
        except Exception:
            pass
    log.close()
