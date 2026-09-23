import os
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return "SBAGOFX Server is running"


@app.route("/api/signal", methods=["POST"])
def signal():
    data = request.get_json()

    print("================================")
    print("SBAGOFX SIGNAL RECEIVED")
    print("================================")
    print(data)
    print("================================")

    return jsonify({
        "status": "success",
        "message": "Signal received by SBAGOFX",
        "signal": data
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)