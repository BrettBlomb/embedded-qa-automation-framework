# mock_servers/mock_rest_server.py

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    """Simple health-check endpoint used by REST tests."""
    return jsonify({"status": "ok"}), 200


@app.route("/status", methods=["GET"])
def status():
    """Extra status endpoint if you want to expand REST tests later."""
    return jsonify({"status": "device-ready"}), 200


if __name__ == "__main__":
    # Bind on 0.0.0.0:5001 so Jenkins can hit http://127.0.0.1:5001/health
    app.run(host="0.0.0.0", port=5001)
