import sys
import time
import os

# maps all of my character inputs to hex using a hashmap
KEY_MAP = {
    'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08, 'f': 0x09,
    'g': 0x0a, 'h': 0x0b, 'i': 0x0c, 'j': 0x0d, 'k': 0x0e, 'l': 0x0f,
    'm': 0x10, 'n': 0x11, 'o': 0x12, 'p': 0x13, 'q': 0x14, 'r': 0x15,
    's': 0x16, 't': 0x17, 'u': 0x18, 'v': 0x19, 'w': 0x1a, 'x': 0x1b,
    'y': 0x1c, 'z': 0x1d, '1': 0x1e, '2': 0x1f, '3': 0x20, '4': 0x21,
    '5': 0x22, '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27,
    ' ': 0x2c, '\n': 0x28, '-': 0x2d, '=': 0x2e, '[': 0x2f, ']': 0x30,
    '\\': 0x31, ';': 0x33, '\'': 0x34, '`': 0x35, ',': 0x36, '.': 0x37,
    '/': 0x38, '_': 0x2d, ':': 0x33, '"': 0x34
}

# this takes the char and converts it into a injectable keyboard input and sends it
def send_key(hid_dev, char):
    # just a basic check to ensure they keys are sendable
    if char.lower() not in KEY_MAP:
        return
    
    code = KEY_MAP[char.lower()]
    
    # checks if the character we are sending needs a shift key press (e.g for uppercase or ':')
    shift_mask = 0x00;
    if (char.isupper() or char == ':'):        
        shift_mask = 0x02 
    else:
        shift_mask = 0x00
    
    # input for the injection (pressing down on the key)
    input = bytes([shift_mask, 0x00, code, 0x00, 0x00, 0x00, 0x00, 0x00])
    hid_dev.write(input)
    hid_dev.flush()
    time.sleep(0.008)  # 8ms is what I found worked well
    
    # input for the injection (releasing the key)
    null_input = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    hid_dev.write(null_input)
    hid_dev.flush()
    time.sleep(0.008)

# sends the string as an inejction
def type_string(hid_device_path, text):
    with open(hid_device_path, 'rb+', buffering=0) as hid:
        for char in text:
            send_key(hid, char)


## DUCKY SCRIPT INTERPRETER ##

MOD_CTRL = 0x01
MOD_SHIFT = 0x02
MOD_ALT = 0x04
MOD_GUI = 0x08  # left windows key

def send_key_combo(hid_dev, modifier: int, char_key: str):
    """Sends a modifier key combination (e.g. GUI + r, CTRL + c)."""
    if char_key.lower() not in KEY_MAP:
        return
    code = KEY_MAP[char_key.lower()]

    # Press combination report
    report = bytes([modifier, 0x00, code, 0x00, 0x00, 0x00, 0x00, 0x00])
    hid_dev.write(report)
    hid_dev.flush()
    time.sleep(0.01)

    # Release all keys report
    null_report = bytes([0x00] * 8)
    hid_dev.write(null_report)
    hid_dev.flush()
    time.sleep(0.01)

# this allows me to run the ducky script for the injection
def execute_ducky_script(hid_dev, script_path):
    # just a standard check to make sure that the path isnt mangled
    if not os.path.exists(script_path):
        print(f"ducky script file not found: {script_path}")
        return

    # executes the script
    print(f"executing ducky script: {script_path}")
    with open(script_path, "r") as f:
        # tgets the current line
        for line in f:
            line = line.strip()
            # ignore blank lines and comments (REM)
            if not line or line.startswith("REM"):
                continue
            
            # gets the current command and respective arguments
            parts = line.split(" ", 1)
            cmd = parts[0].upper()
            if len(parts) > 1:
                args = parts[1] 
            else:
                args = ""

            # executes the command
            if cmd == "DELAY":
                delay_ms = float(args) / 1000.0
                time.sleep(delay_ms)
            elif cmd == "STRING":
                type_string(hid_dev, args)
            elif cmd == "ENTER":
                send_key(hid_dev, "\n")
            # GUI and Windows both need key combos e.g Win + R 
            elif cmd in ["GUI", "WINDOWS"]:
                    # handles "GUI r", "WINDOWS r" etc
                    if args:
                        send_key_combo(hid_dev, MOD_GUI, args[0])
                    else:
                        # press of the Windows key
                        send_key_combo(hid_dev, MOD_GUI, ' ')
         
if __name__ == "__main__":
    # i added this code because I KEPT RUNNING IT WITH OUT INITIALISING THE HID
    hid_path = "/dev/hidg0"
    if not os.path.exists(hid_path):
        print(f"Error: hid device does not exist, did you run enable-usb-hid.sh")
        sys.exit(1)

    # decyphers the ducky script to run the code
    ducky_script_file = "injection.txt"
    # the buffering is set to 0 so everything is instantly sent
    with open(hid_path, "rb+", buffering=0) as hid_device:
        execute_ducky_script(hid_device, ducky_script_file)