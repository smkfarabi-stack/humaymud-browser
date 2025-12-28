import asyncio
import httpx
from playwright.async_api import async_playwright
from duckduckgo_search import DDGS
from googlesearch import search as google_search
from .gemini_analyzer import GeminiAnalyzer

analyzer = GeminiAnalyzer()

# High-quality repositories to prioritize
FREE_REPOS = [
    "archive.org", "gutenberg.org", "libgen.is", "libgen.rs", 
    "annas-archive.org", "pdfdrive.com", "scholar.google.com"
]

PAID_REPOS = [
    "amazon.com", "springer.com", "wiley.com", "sciencedirect.com", 
    "books.google.com", "oreilly.com", "shop.elsevier.com"
]

async def verify_link_is_file(client, url, expected_type):
    """
    Layer 1: Checks if the link points directly to a binary file.
    """
    try:
        response = await client.head(url, timeout=4, follow_redirects=True)
        content_type = response.headers.get("content-type", "").lower()
        content_disp = response.headers.get("content-disposition", "").lower()

        # Check for direct file signatures
        if expected_type in content_type or "application/pdf" in content_type:
            return 100, "Direct File Link"
        
        if f".{expected_type}" in content_disp or "attachment" in content_disp:
            return 100, "Direct Download"
            
        return 0, None
    except:
        return 0, None

async def analyze_single_result(context, result, filetype):
    """
    Layer 2: Deep analysis of the webpage using Playwright & Gemini.
    """
    if not result.get('href'): return None
    url = result['href']
    
    # --- LEVEL 1: SPEED CHECK (HEAD Request) ---
    async with httpx.AsyncClient(verify=False) as client:
        direct_score, direct_reason = await verify_link_is_file(client, url, filetype)
        if direct_score == 100:
            return {
                "title": result.get('title', 'Direct File'),
                "source_url": url,
                "snippet": "✅ Verified Direct Download Link",
                "download_link": url,
                "trust_score": 98,
                "type": filetype.upper()
            }

    # --- LEVEL 2: DEEP PAGE AUDIT (AI) ---
    page = await context.new_page()
    try:
        # Optimization: Block images/media to load fast
        await page.route("**/*.{png,jpg,jpeg,gif,mp4,ad,track}", lambda route: route.abort())
        
        try:
            await page.goto(url, timeout=9000, wait_until="domcontentloaded")
        except:
            await page.close()
            return None

        # Extract text for AI
        page_text = await page.inner_text("body")
        
        # AI Audit
        audit = analyzer.audit_page_content(url, page_text)
        
        if audit['status'] == "ACCEPTED":
            return {
                "title": result.get('title', await page.title()),
                "source_url": url,
                "snippet": audit['reason'],
                "download_link": url,
                "trust_score": audit['confidence'],
                "type": "WEB"
            }

    except Exception:
        pass
    finally:
        await page.close()
    
    return None

def get_search_query(filename, filetype, mode):
    if mode == "free":
        sites = " OR ".join([f"site:{site}" for site in FREE_REPOS])
        return f"({sites}) intitle:\"{filename}\" {filetype}"
    else:
        sites = " OR ".join([f"site:{site}" for site in PAID_REPOS])
        return f"\"{filename}\" book {filetype} (buy OR purchase OR download) ({sites})"

async def search_and_analyze(filename, filetype, mode):
    query = get_search_query(filename, filetype, mode)
    raw_links = []
    
    # 1. Fetch Links (DDG + Google Fallback)
    try:
        ddgs = DDGS()
        raw_links = list(ddgs.text(query, max_results=10, backend="html"))
    except: pass
        
    if not raw_links:
        try:
            g_gen = google_search(query, num_results=8, advanced=True)
            for res in g_gen:
                raw_links.append({"title": res.title, "href": res.url})
        except: pass

    # 2. Parallel Processing
    verified_results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        
        # Create tasks for all links
        tasks = [analyze_single_result(context, res, filetype) for res in raw_links]
        results = await asyncio.gather(*tasks)
        
        verified_results = [r for r in results if r is not None]
        await browser.close()

    # Sort best results first
    verified_results.sort(key=lambda x: x['trust_score'], reverse=True)
    return verified_results