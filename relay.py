from flask import Flask, request, jsonify
import time
import json
import os

app = Flask(__name__)

ALERT_LOG_FILE = "alerts.json"


def save_alert(alert_data):
    """
    Save alerts to a local JSON file.
    """
    if os.path.exists(ALERT_LOG_FILE):
        with open(ALERT_LOG_FILE, "r") as f:
            alerts = json.load(f)
    else:
        alerts = []

    alerts.append(alert_data)

    with open(ALERT_LOG_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


@app.route("/alert", methods=["POST"])
def alert():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    item = data.get("item", "Unknown item")
    room = data.get("room", "Unknown room")
    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    alert_data = {
        "item": item,
        "room": room,
        "time": ts
    }

    print("\n========== EDC ALERT ==========")
    print(f"Item: {item}")
    print(f"Last seen: {room}")
    print(f"Time: {ts}")
    print("================================\n")

    save_alert(alert_data)

    return jsonify({"status": "alert received"}), 200


@app.route("/alerts", methods=["GET"])
def get_alerts():
    """
    View stored alerts.
    """
    if os.path.exists(ALERT_LOG_FILE):
        with open(ALERT_LOG_FILE, "r") as f:
            alerts = json.load(f)
        return jsonify(alerts), 200
    else:
        return jsonify([]), 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"system": "running"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)