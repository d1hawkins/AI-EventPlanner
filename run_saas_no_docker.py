from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import uvicorn

app = FastAPI(title="AI Event Planner SaaS")

# Mount static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# Create templates
templates = Jinja2Templates(directory="app/web/static/saas")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/static/saas/index.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
