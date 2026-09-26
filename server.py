import os
from datetime import datetime, timezone

from flask import Flask, request, jsonify

app = Flask(__name__)


# ============================================================
# TEMPORARY DEVICE STORAGE
# ============================================================
# This stores registered devices while the Render server is
# running.
#
# Later we will move this to a proper database so devices
# survive server restarts/redeployments.
# ============================================================

devices = {}


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return "SBAGOFX Server is running"


# ============================================================
# REGISTER ANDROID DEVICE
# ============================================================

@app.route("/api/devices", methods=["POST"])
def register_device():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data received"
        }), 400

    installation_id = data.get("installationId")
    platform = data.get("platform", "unknown")
    app_version = data.get("appVersion", "unknown")

    if not installation_id:

        return jsonify({
            "status": "error",
            "message": "installationId is required"
        }), 400

    now = datetime.now(timezone.utc).isoformat()

    devices[installation_id] = {
        "installationId": installation_id,
        "platform": platform,
        "appVersion": app_version,
        "lastSeen": now
    }

    print("================================")
    print("SBAGOFX DEVICE REGISTERED")
    print("================================")
    print("Installation ID:", installation_id)
    print("Platform:", platform)
    print("App Version:", app_version)
    print("Last Seen:", now)
    print("Total Devices:", len(devices))
    print("================================")

    return jsonify({
        "status": "success",
        "message": "Device registered successfully",
        "installationId": installation_id,
        "platform": platform,
        "appVersion": app_version,
        "lastSeen": now
    }), 200


# ============================================================
# RECEIVE TRADING SIGNAL FROM MT5
# ============================================================

@app.route("/api/signal", methods=["POST"])
def signal():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "status": "error",
            "message": "No JSON signal received"
        }), 400

    print("================================")
    print("SBAGOFX SIGNAL RECEIVED")
    print("================================")
    print(data)
    print("================================")

    return jsonify({
        "status": "success",
        "message": "Signal received by SBAGOFX",
        "signal": data
    }), 200


# ============================================================
# SERVER START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )