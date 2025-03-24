import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.auth.router import router as auth_router
from app.web.router import router as web_router
from app.subscription.router import router as subscription_router
from app.agents.api_router import router as agent_router
from app.middleware.tenant import tenant_middleware
from app.db.base import engine

# Database tables are created by migrations
# Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="AI Event Planner SaaS", description="AI-powered event planning SaaS platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware
app.middleware("http")(tenant_middleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
app.mount("/saas", StaticFiles(directory="app/web/static/saas"), name="saas_static")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(web_router, prefix="/api", tags=["api"])
app.include_router(subscription_router, prefix="/subscription", tags=["subscription"])
app.include_router(agent_router, prefix="/api", tags=["agents"])

# Templates
templates = Jinja2Templates(directory="app/web/static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the main HTML page.
    
    Args:
        request: FastAPI request
        
    Returns:
        HTML response
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run("app.main_saas:app", host=host, port=port, reload=True)
