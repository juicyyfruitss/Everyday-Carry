import serial
import json
import time
import requests  # only if using PC relay via HTTP

# ---------------- CONFIG ----------------
SERIAL_PORT = '/dev/ttyUSB0'  # check with ls /dev/ttyUSB*
BAUD_RATE = 115200
LAST_SEEN_FILE = 'last_seen.json'

# Items you want to monitor for alerts (can be MAC addresses or names)
MONITORED_ITEMS = {
    "48:87:2d:9d:56:a3": "Wallet",
    "48:87:2d:9d:56:94": "Keys",
}

# PC Relay endpoint for alerts
PC_RELAY_URL = "http://192.168.1.139:5000/alert"  # replace with your PC relay endpoint




last_alert_time = {}

# ---------------- INIT ----------------
# Load or create last_seen.json
try:
    with open(LAST_SEEN_FILE, 'r') as f:
        last_seen = json.load(f)
except:
    last_seen = {}

# Open Serial connection to ESP32
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Wait for Serial to stabilize

print("Front Door Tracker running...")

# ---------------- FUNCTIONS ----------------
def notify_missing(item_name, last_room):
    """
    Send SMS using Twilio.
    """
    now = time.time()

    # Prevent repeated alerts
    if item_name in last_alert_time:
        if now - last_alert_time[item_name] < ALERT_COOLDOWN:
            return

    message_body = f"Missing Item Alert\n{item_name} last seen in {last_room}"

    print("ALERT:", message_body)

    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print("SMS sent! SID:", message.sid)
        last_alert_time[item_name] = now
    except Exception as e:
        print("Failed to send SMS:", e)

# ---------------- MAIN LOOP ----------------
while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            continue
        if not line.startswith("{"):  # skip non-JSON lines
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

        print(f"Detected {MONITORED_ITEMS.get(item_mac, item_mac)} at {room}")

        # Only trigger alert if this is the Front Door
        if room == "Front Door":
            # Check monitored items
            for mac, name in MONITORED_ITEMS.items():
                last_room = last_seen.get(mac)
                if last_room and last_room != "Front Door":
                    notify_missing(name, last_room)

    except Exception as e:
        print("Error processing line:", e)

