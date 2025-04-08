from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

def extract_emails_from_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=60000)
        content = page.content()
        browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        emails = re.findall(r"[\w\.-]+@[\w\.-]+", text)
        return list(set(emails))

@app.route('/extract-emails', methods=['POST'])
def extract_emails():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    try:
        emails = extract_emails_from_url(url)
        return jsonify({"emails": emails})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # default for local testing
    app.run(host='0.0.0.0', port=port)
