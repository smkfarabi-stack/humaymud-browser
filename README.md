# 🌊 HumayMud: Deep Ocean Search Engine

HumayMud is an AI-powered vertical search engine designed to locate and verify academic resources (PDF/EPUB). Unlike standard search engines, it uses a multi-layer verification system to ensure links are safe before the user clicks.

## 🚀 Features
* **🛡️ Deep Packet Inspection:** Verifies binary file signatures (HTTP Headers) to confirm files are real PDFs/EPUBs.
* **🤖 AI Verification:** Integrated **Google Gemini 1.5** to visually audit landing pages and filter out spam/fake download buttons.
* **🕵️ Stealth Browsing:** Uses **Playwright** (Headless Chromium) to navigate JavaScript-heavy repositories without detection.
* **⚡ Real-Time Async:** Built on **FastAPI** to handle concurrent searches with a non-blocking architecture.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Backend:** FastAPI, Uvicorn
* **Browser Engine:** Playwright
* **AI:** Google Gemini API
* **Frontend:** HTML5, TailwindCSS

## 📦 How to Run Locally
1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/smkfarabi-stack/humaymud-browser.git](https://github.com/smkfarabi-stack/humaymud-browser.git)
    cd humaymud-browser
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```
3.  **Set API Key:**
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```
4.  **Run Server:**
    ```bash
    python main.py
    ```
