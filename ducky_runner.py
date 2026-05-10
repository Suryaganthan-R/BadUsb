import time
import keymap
import sys
import os

# Set the working directory to the script's actual folder
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

HID_DEV = "/dev/hidg0"
SCRIPTS_DIR = os.path.join(script_dir, "ducky_scripts")

def send_report(report):
    with open(HID_DEV, 'rb+') as fd:
        fd.write(report.encode('latin-1'))

def press_key(key_name):
    if key_name in keymap.keys:
        mod, code = keymap.keys[key_name]
        send_report(mod + '\x00' + code + '\x00' * 5)
        send_report('\x00' * 8)
        time.sleep(0.01)
    else:
        print(f"Key '{key_name}' unknown.")

def type_string(text):
    for char in text:
        press_key(char)

def parse_line(line):
    line = line.strip()
    if not line or line.startswith("REM"):
        return
    parts = line.split(' ')
    cmd = parts[0].upper()
    args = " ".join(parts[1:])

    if cmd == "STRING":
        type_string(args)
    elif cmd == "DELAY":
        time.sleep(int(args) / 1000)
    elif cmd == "ENTER":
        press_key("ENTER")
    elif cmd in ["GUI", "WINDOWS"]:
        press_key("GUI_R")
    elif cmd == "ALT" and args.upper() == "F4":
        press_key("ALT_F4")
    elif cmd == "TAB":
        press_key("TAB")
    elif cmd in keymap.keys:
        press_key(cmd)

def get_menu_choice():
    if not os.path.exists(SCRIPTS_DIR):
        os.makedirs(SCRIPTS_DIR)

    # Get all .txt files in the scripts folder
    scripts = sorted([f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.txt')])

    if not scripts:
        print(f"\n[!] No scripts found in {SCRIPTS_DIR}")
        return None

    print("\n" + "="*35)
    print("    ASTRA KERNEL PAYLOADS")
    print("="*35)
    for i, script in enumerate(scripts, 1):
        print(f" {i:2} > {script}")
    print("="*35)

    try:
        choice = input("\nSelect payload # (or 'q' to quit): ")
        if choice.lower() == 'q': return None
        idx = int(choice) - 1
        if 0 <= idx < len(scripts):
            return os.path.join(SCRIPTS_DIR, scripts[idx])
        else:
            print("[!] Invalid number.")
            return None
    except ValueError:
        print("[!] Please enter a number.")
        return None

def run_payload(full_path):
    print(f"\n[+] Parsing {os.path.basename(full_path)}...")

    # --- DYNAMIC INTERACTIVE LOGIC ---
    replace_val = None
    script_name = os.path.basename(full_path)

    try:
        # BROADER IP TRIGGER: Works for Exfil, Reverse, or Connection scripts
        if any(keyword in script_name for keyword in ["Exfil", "Reverse", "Connection"]):
            replace_val = input("\n[?] Enter Pi IP for connection: ")

        # Works for any script containing "Virus"
        elif "Virus" in script_name:
            u_input = input("\n[?] Enter number of prompts (0 for unlimited): ")
            replace_val = "99999" if u_input == "0" else u_input

        # Works for any script containing "Speak"
        elif "Speak" in script_name:
            u_input = input("\n[?] What should the Astra Kernel say? : ")
            replace_val = u_input if u_input.strip() else "Astra Kernel is watching you."

    except KeyboardInterrupt:
        print("\n[!] Input cancelled.")
        return

    # ---------------------------------

    try:
        with open(full_path, 'r') as f:
            for line in f:
                # Universal replacement logic for placeholders
                if replace_val:
                    line = line.replace("REPLACE_IP", replace_val)
                    line = line.replace("REPLACE_COUNT", replace_val)
                    line = line.replace("REPLACE_VOICE", replace_val)
                parse_line(line)
        print("[+] Execution Complete.")
    except Exception as e:
        print(f"[!] Error: {e}")

def main():
    try:
        if len(sys.argv) > 1:
            payload = os.path.join(SCRIPTS_DIR, sys.argv[1])
            if os.path.exists(payload):
                run_payload(payload)
            else:
                print(f"[!] File {sys.argv[1]} not found in {SCRIPTS_DIR}")
        else:
            selected_script = get_menu_choice()
            if selected_script:
                run_payload(selected_script)
    except KeyboardInterrupt:
        print("\n\n[!] ASTRA_KERNEL: Connection Severed.")
        print("[!] Ghosting the session... Stay undetected.")
        sys.exit(0)

if __name__ == "__main__":
    if not sys.stdin.isatty():
        os.system("sudo /home/astrabot/BadUsb/setup_gadget.sh")
        time.sleep(15)
        default_bot = os.path.join(SCRIPTS_DIR, "01_Astra_Intro.txt")
        if os.path.exists(default_bot):
            run_payload(default_bot)
    else:
        main()
