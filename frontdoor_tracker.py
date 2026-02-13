import serial
import json
import time
import threading
from postmarker.core import PostmarkClient
from pathlib import Path

# ---------------- CONFIG ----------------
SERIAL_PORT = '/dev/ttyUSB0'  # or 'COM3' on Windows
BAUD_RATE = 115200
LAST_SEEN_FILE = Path('last_seen.json')
MONITORED_FILE = Path('monitored_items.json')  # Persistent monitored items
ALERT_COOLDOWN = 60  # seconds between repeated alerts

# ---------------- POSTMARK SETUP ----------------
POSTMARK_TOKEN = "d7499ce1-f3d0-4f2b-aa85-1ca332eb1e8c"
SENDER_EMAIL = "dlr060@email.latech.edu"

postmark = PostmarkClient(server_token=POSTMARK_TOKEN)

# ---------------- LOAD OR INIT DATA ----------------
# Load last seen info
if LAST_SEEN_FILE.exists():
    with open(LAST_SEEN_FILE, 'r') as f:
        last_seen = json.load(f)
else:
    last_seen = {}

# Load monitored items
if MONITORED_FILE.exists():
    with open(MONITORED_FILE, 'r') as f:
        MONITORED_ITEMS = json.load(f)
else:
    # Default example
    MONITORED_ITEMS = {
        "48:87:2d:9d:56:a3": "Wallet",
        "48:87:2d:9d:56:94": "Keys",
    }

last_alert_time = {}

# ---------------- SERIAL SETUP ----------------
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Tracker running on port", SERIAL_PORT)
except Exception as e:
    print("Failed to open serial port:", e)
    ser = None

# ---------------- FUNCTIONS ----------------
def save_monitored_items():
    """Save the monitored items to JSON file."""
    with open(MONITORED_FILE, 'w') as f:
        json.dump(MONITORED_ITEMS, f, indent=2)

def add_monitored_item(mac: str, name: str):
    """Add a new MAC-addressed item to monitoring list."""
    MONITORED_ITEMS[mac] = name
    save_monitored_items()
    print(f"Added {name} ({mac}) to monitored items")

def notify_missing(item_name: str, last_room: str, user_email: str):
    """Send an email alert if the item is missing."""
    now = time.time()
    if item_name in last_alert_time and now - last_alert_time[item_name] < ALERT_COOLDOWN:
        return

    message_body = f"Missing Item Alert\n{item_name} last seen in {last_room}"
    print("ALERT:", message_body)

    try:
        postmark.emails.send(
            From=SENDER_EMAIL,
            To=user_email,
            Subject=f"{item_name} Left Behind",
            HtmlBody=f"<strong>{message_body}</strong>",
            TextBody=message_body
        )
        print(f"Email sent to {user_email}")
        last_alert_time[item_name] = now
    except Exception as e:
        print("Failed to send email:", e)

# ---------------- MAIN TRACKING LOOP ----------------
def track_loop(user_email: str):
    if not ser:
        print("Serial port not initialized. Exiting tracking loop.")
        return

    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line or not line.startswith("{"):
                continue

            data = json.loads(line)
            item_mac = data.get("item")
            room = data.get("room")
            if not item_mac or not room:
                continue

            # Update last seen
            last_seen[item_mac] = room
            with open(LAST_SEEN_FILE, 'w') as f:
                json.dump(last_seen, f, indent=2)

            item_name = MONITORED_ITEMS.get(item_mac, item_mac)
            print(f"Detected {item_name} at {room}")

            # Alert logic: only alert if item is away from Front Door
            if room != "Front Door" and item_mac in MONITORED_ITEMS:
                notify_missing(item_name, room, user_email)

        except Exception as e:
            print("Error processing line:", e)

# ---------------- THREAD TO RUN TRACKING ----------------
def start_tracking(user_email: str):
    thread = threading.Thread(target=track_loop, args=(user_email,), daemon=True)
    thread.start()
    print("Tracking thread started.")

# ---------------- EXAMPLE USAGE ----------------
if __name__ == "__main__":
    user_email = "dlr060@email.latech.edu"  # Replace with dynamic Kivy user email
    start_tracking(user_email)

    # Example: dynamically add a new monitored item
    # add_monitored_item("00:11:22:33:44:55", "Backpack")

    try:
        while True:
            time.sleep(5)  # Keep main thread alive
    except KeyboardInterrupt:
        print("Exiting tracker.")
