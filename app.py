"""
HTTP Request Analyzer - Flask Web Application
Provides a web-based graphical interface and REST API for analyzing HTTP requests.
"""

from flask import Flask, render_template, request, jsonify
from analyzer import analyze_request

app = Flask(__name__)


@app.route("/")
def index():
    """Renders the main HTTP Request Analyzer web interface."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    API endpoint to analyze an HTTP request.
    Expects JSON payload with:
      - url (str)
      - method (str, optional)
      - headers (dict, optional)
      - data (str, optional)
      - json_data (dict/list, optional)
      - timeout (float, optional)
    """
    payload = request.get_json(silent=True) or {}
    url = payload.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "error_type": "Invalid Input",
            "error_message": "Please enter a valid URL."
        }), 400

    method = payload.get("method", "GET").upper()
    headers = payload.get("headers") or {}
    body_data = payload.get("data")
    json_data = payload.get("json_data")
    timeout = float(payload.get("timeout", 10.0))

    # Perform analysis
    result = analyze_request(
        url=url,
        method=method,
        headers=headers,
        data=body_data,
        json_data=json_data,
        timeout=timeout
    )

    return jsonify(result)


@app.route("/api/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "HTTP Request Analyzer"})


if __name__ == "__main__":
    print("\nStarting HTTP Request Analyzer Web UI on http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server.\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
