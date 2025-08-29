from flask import Flask, request, jsonify
import re
import requests

app = Flask(__name__)

# ✅ Root endpoint
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "✅ Web Email Extractor API is live",
        "usage": "Send a POST request to /extract-emails with { 'urls': ['https://example.com'] }"
    })

# ✅ Email extractor endpoint
@app.route("/extract-emails", methods=["POST"])
def extract_emails():
    data = request.get_json()
    urls = data.get("urls", [])
    results = {}

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            # Find emails with regex
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
            results[url] = list(set(emails))  # Remove duplicates
        except Exception as e:
            results[url] = {"error": str(e)}

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
