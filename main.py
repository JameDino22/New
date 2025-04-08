from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

def extract_emails_from_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set to False for visible browsing
        page = browser.new_page()

        # Set up user-agent and other headers to simulate a real browser
        page.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Navigate to the page
        page.goto(url)

        # You can optionally wait for some elements to load
        page.wait_for_selector("body")

        # Extract emails (or do other scraping tasks)
        emails = page.evaluate('''() => {
            let emailArray = [];
            let emailRegex = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
            let pageText = document.body.innerText;
            let matches = pageText.match(emailRegex);
            if (matches) {
                emailArray = matches;
            }
            return emailArray;
        }''')

        browser.close()
        return emails

@app.route("/extract-emails", methods=["POST"])
def extract_emails():
    data = request.get_json()
    urls = data.get("urls", [])

    if not urls or not isinstance(urls, list):
        return jsonify({"error": "Please provide a list of URLs in 'urls' key"}), 400

    results = {}

    for url in urls:
        try:
            emails = extract_emails_from_url(url)  # Your Playwright logic here
            results[url] = emails
        except Exception as e:
            results[url] = {"error": str(e)}

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
