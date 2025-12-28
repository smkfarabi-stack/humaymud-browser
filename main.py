import os
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.engine import search_and_analyze

# Initialize App
app = FastAPI(title="HumayMud Browser")

# Ensure directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("core", exist_ok=True)

# Mount Static Files & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search")
async def search_post(
    request: Request,
    filename: str = Form(...),
    filetype: str = Form(...),
    license: str = Form(...)  # 'free' or 'paid'
):
    print(f"🌊 HumayMud Scanning for: {filename} [{filetype}] ({license})")
    
    # Trigger the deep search engine
    results = await search_and_analyze(filename, filetype, license)
    
    return JSONResponse({
        "status": "success",
        "results": results
    })

if __name__ == "__main__":
    # Check for API Key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ WARNING: GEMINI_API_KEY not set. Deep AI analysis will fail.")
        
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)