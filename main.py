
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

def extract_emails_from_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        content = page.content()
        browser.close()
    
    # Simple regex to find emails
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return list(set(re.findall(email_pattern, content)))

# ✅ Health check route
@app.route("/", methods=["GET"])
def home():
    return "✅ Email Extractor is Live!"

# ✅ Bulk email extraction route
@app.route("/extract-emails", methods=["POST"])
def extract_emails():
    data = request.get_json()
    urls = data.get("urls", [])

    if not urls or not isinstance(urls, list):
        return jsonify({"error": "Please provide a list of URLs in 'urls' key"}), 400

    results = {}

    for url in urls:
        try:
            emails = extract_emails_from_url(url)
            results[url] = emails
        except Exception as e:
            results[url] = {"error": str(e)}

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
