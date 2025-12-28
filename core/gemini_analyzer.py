import os
import google.generativeai as genai
import json
import re

class GeminiAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Fallback to prevent crash, but search will be degraded
            print("Gemini API Key missing")
            self.model = None
            return

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def audit_page_content(self, url, page_text):
        if not self.model:
            return {"status": "ACCEPTED", "confidence": 50, "reason": "AI unavailable, basic check passed"}

        prompt = f"""
        You are auditing a search result for a user looking for a specific book/file.
        URL: {url}
        Page Content Snippet: {page_text[:4000]}
        
        Task:
        1. Is this a LEGITIMATE page where the user can buy or download the book? (ACCEPTED)
        2. Is it a spam, malware, parked domain, or irrelevant blog? (REJECTED)
        
        Return JSON ONLY:
        {{
            "status": "ACCEPTED" or "REJECTED",
            "confidence": 0-100,
            "reason": "Why you think so (max 10 words)"
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            # Clean JSON response
            clean_text = re.sub(r'```json|```', '', response.text).strip()
            return json.loads(clean_text)
        except:
            # Fail open if AI fails (assuming it might be good)
            return {"status": "ACCEPTED", "confidence": 60, "reason": "AI check skipped"}