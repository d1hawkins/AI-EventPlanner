import os
import time
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.router import router as auth_router
from app.web.router import router as web_router
from app.subscription.router import router as subscription_router
from app.agents.api_router import router as agent_router
from app.middleware.tenant import tenant_middleware
from app.db.base import engine
from app.config import validate_config
from app.utils.logging_utils import setup_logger, log_api_request, flush_telemetry

# Set up logger for the SaaS application
logger = setup_logger(
    name="saas",
    log_level="DEBUG",
    enable_app_insights=True,
    app_insights_level="INFO",
    component="saas"
)

# Database tables are created by migrations
# Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="AI Event Planner SaaS", description="AI-powered event planning SaaS platform")

# Request timing middleware
class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get organization ID from request state if available
        organization_id = getattr(request.state, "organization_id", None)
        
        # Process the request
        response = await call_next(request)
        
        # Calculate request duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Get user ID from request if available
        user_id = None
        try:
            if hasattr(request, "user") and hasattr(request, "scope") and "user" in request.scope:
                user = request.user
                if user and hasattr(user, "id"):
                    user_id = user.id
        except (AttributeError, AssertionError):
            # Handle cases where AuthenticationMiddleware is not installed
            user_id = None
        
        # Log the request
        log_api_request(
            logger=logger,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            organization_id=organization_id
        )
        
        return response

# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
app.add_middleware(RequestTimingMiddleware)

# Add tenant middleware
app.middleware("http")(tenant_middleware)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Validate configuration on startup and initialize logging.
    """
    try:
        validate_config()
        logger.info("Configuration validation successful.")
        logger.info(f"Application starting in {os.getenv('ENVIRONMENT', 'development')} environment")
        
        # Log application version
        app_version = os.getenv("APP_VERSION", "1.0.0")
        logger.info(f"Application version: {app_version}")
        
        # Log instrumentation key availability
        if os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY"):
            logger.info("Azure Application Insights is configured")
        else:
            logger.warning("Azure Application Insights is not configured - telemetry will not be sent")
            
    except ValueError as e:
        logger.error(f"Configuration validation error: {str(e)}")
        # Log the error but don't crash the application
        # This allows the application to start but certain features may be disabled

@app.on_event("shutdown")
async def shutdown_event():
    """
    Perform cleanup on application shutdown.
    """
    logger.info("Application shutting down")
    
    # Flush any pending telemetry
    flush_telemetry()

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
    port = int(os.getenv("PORT", "8002"))
    
    uvicorn.run("app.main_saas:app", host=host, port=port, reload=True)
