import pywinusb.hid as hid

VID = 0x1EA7
PID = 0x0169

print(f"Scanning HID interfaces for VID=0x{VID:04X} PID=0x{PID:04X}\n")

devices = hid.HidDeviceFilter(vendor_id=VID, product_id=PID).get_devices()

if not devices:
    print("No devices found. Is the macropad plugged in?")
else:
    for i, d in enumerate(devices):
        print(f"--- Device {i} ---")
        print(f"  product       : {d.product_name}")
        print(f"  vendor        : {d.vendor_name}")
        print(f"  serial        : {d.serial_number}")
        print(f"  device_path   : {d.device_path}")
        try:
            d.open()
            print(f"  usage_page    : 0x{d.hid_caps.usage_page:04X}")
            print(f"  usage         : 0x{d.hid_caps.usage:04X}")
            print(f"  input_len     : {d.hid_caps.input_report_byte_length}")
            print(f"  output_len    : {d.hid_caps.output_report_byte_length}")
            print(f"  feature_len   : {d.hid_caps.feature_report_byte_length}")
            d.close()
        except Exception as e:
            print(f"  open error    : {e}")
        print()
    print(f"Total: {len(devices)} interfaces")
