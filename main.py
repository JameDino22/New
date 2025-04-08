
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

# ✅ Homepage route (user interface)
@app.route("/", methods=["GET"])
def home():
    return """
    <!doctype html>
    <html>
    <head>
        <title>Email Extractor</title>
        <style>
            body { font-family: sans-serif; max-width: 600px; margin: 40px auto; }
            input, button { padding: 10px; font-size: 16px; width: 100%; margin-top: 10px; }
            #result { margin-top: 20px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>📧 Web Email Extractor</h1>
        <input type="text" id="urlInput" placeholder="Enter website URL (e.g. https://example.com)">
        <button onclick="extractEmails()">Extract Emails</button>
        <div id="result"></div>

        <script>
        async function extractEmails() {
            const url = document.getElementById("urlInput").value;
            const resultDiv = document.getElementById("result");
            resultDiv.textContent = "🔄 Extracting emails...";
            
            try {
                const res = await fetch("/extract-emails", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url: url })
                });

                const data = await res.json();
                resultDiv.textContent = data.emails.length
                    ? `✅ Found ${data.emails.length} email(s):\n\n` + data.emails.join("\n")
                    : "❌ No emails found.";
            } catch (err) {
                resultDiv.textContent = "🚫 Error: " + err.message;
            }
        }
        </script>
    </body>
    </html>
    """

# ✅ Email extraction route
@app.route("/extract-emails", methods=["POST"])
def extract_emails():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=60000)
        content = page.content()
        browser.close()

    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content)
    return jsonify({"emails": list(set(emails))})

if __name__ == "__main__":
    app.run(debug=True)
