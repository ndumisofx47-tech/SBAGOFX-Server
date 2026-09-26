import json
import os
from datetime import datetime, timezone

from flask import Flask, request, jsonify

import firebase_admin
from firebase_admin import credentials, messaging


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# TEMPORARY DEVICE STORAGE
# ============================================================

devices = {}


# ============================================================
# FIREBASE ADMIN INITIALIZATION
# ============================================================

def initialize_firebase():

    if firebase_admin._apps:
        print("================================")
        print("FIREBASE ADMIN ALREADY INITIALIZED")
        print("================================")
        return

    service_account_json = os.environ.get(
        "FIREBASE_SERVICE_ACCOUNT_JSON"
    )

    if not service_account_json:

        print("================================")
        print("FIREBASE ADMIN INITIALIZATION FAILED")
        print("================================")
        print(
            "FIREBASE_SERVICE_ACCOUNT_JSON is missing"
        )
        print("================================")

        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_JSON environment variable is missing"
        )

    try:

        service_account_info = json.loads(
            service_account_json
        )

        credential = credentials.Certificate(
            service_account_info
        )

        firebase_admin.initialize_app(
            credential
        )

        print("================================")
        print("FIREBASE ADMIN INITIALIZED")
        print("================================")

    except Exception as e:

        print("================================")
        print("FIREBASE ADMIN INITIALIZATION FAILED")
        print("================================")
        print(str(e))
        print("================================")

        raise


initialize_firebase()


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return "SBAGOFX Server is running", 200


# ============================================================
# DEVICE REGISTRATION
# ============================================================

@app.route(
    "/api/devices",
    methods=["POST"]
)
def register_device():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "status": "error",

            "message":
                "No JSON data received"

        }), 400

    installation_id = data.get(
        "installationId"
    )

    platform = data.get(
        "platform",
        "unknown"
    )

    app_version = data.get(
        "appVersion",
        "unknown"
    )

    if not installation_id:

        return jsonify({

            "status": "error",

            "message":
                "installationId is required"

        }), 400

    now = datetime.now(
        timezone.utc
    ).isoformat()

    devices[installation_id] = {

        "installationId":
            installation_id,

        "platform":
            platform,

        "appVersion":
            app_version,

        "lastSeen":
            now
    }

    print("================================")
    print("SBAGOFX DEVICE REGISTERED")
    print("================================")

    print(
        "Installation ID:",
        installation_id
    )

    print(
        "Platform:",
        platform
    )

    print(
        "App Version:",
        app_version
    )

    print(
        "Last Seen:",
        now
    )

    print(
        "Total Devices:",
        len(devices)
    )

    print("================================")

    return jsonify({

        "status":
            "success",

        "message":
            "Device registered successfully",

        "installationId":
            installation_id,

        "platform":
            platform,

        "appVersion":
            app_version,

        "lastSeen":
            now

    }), 200


# ============================================================
# RECEIVE MT5 SIGNAL
# ============================================================

@app.route(
    "/api/signal",
    methods=["POST"]
)
def signal():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "status":
                "error",

            "message":
                "No JSON signal received"

        }), 400

    print("================================")
    print("SBAGOFX SIGNAL RECEIVED")
    print("================================")

    print(data)

    print("================================")

    return jsonify({

        "status":
            "success",

        "message":
            "Signal received by SBAGOFX",

        "signal":
            data

    }), 200


# ============================================================
# TEST PUSH NOTIFICATION
# ============================================================

@app.route(
    "/api/test-alert",
    methods=["POST"]
)
def test_alert():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "status":
                "error",

            "message":
                "No JSON data received"

        }), 400

    installation_id = data.get(
        "installationId"
    )

    if not installation_id:

        return jsonify({

            "status":
                "error",

            "message":
                "installationId is required"

        }), 400

    if installation_id not in devices:

        return jsonify({

            "status":
                "error",

            "message":
                "Device is not registered",

            "installationId":
                installation_id

        }), 404

    try:

        message = messaging.Message(

            notification=messaging.Notification(

                title="SBAGOFX SELL ALERT",

                body=(
                    "XAUUSD M5 - "
                    "Shift confirmed"
                )
            ),

            data={

                "symbol":
                    "XAUUSD",

                "timeframe":
                    "M5",

                "direction":
                    "SELL",

                "shiftLevel":
                    "3648.20"

            },

            fid=installation_id
        )

        response = messaging.send(
            message
        )

        print("================================")
        print("SBAGOFX TEST PUSH SENT")
        print("================================")

        print(
            "Installation ID:",
            installation_id
        )

        print(
            "Firebase Response:",
            response
        )

        print("================================")

        return jsonify({

            "status":
                "success",

            "message":
                "Test push notification sent",

            "firebaseResponse":
                response,

            "installationId":
                installation_id

        }), 200

    except Exception as e:

        print("================================")
        print("SBAGOFX PUSH FAILED")
        print("================================")

        print(
            "Error:",
            str(e)
        )

        print("================================")

        return jsonify({

            "status":
                "error",

            "message":
                "Failed to send push notification",

            "error":
                str(e)

        }), 500


# ============================================================
# ROUTE DIAGNOSTIC
# ============================================================

@app.route(
    "/api/routes",
    methods=["GET"]
)
def list_routes():

    routes = []

    for rule in app.url_map.iter_rules():

        routes.append({

            "route":
                str(rule),

            "methods":
                sorted(
                    list(rule.methods)
                )

        })

    return jsonify({

        "status":
            "success",

        "routes":
            routes

    }), 200


# ============================================================
# START SERVER
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