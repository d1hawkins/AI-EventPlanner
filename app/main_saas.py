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
from app.web.router_additional import router as additional_router
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
        # Skip detailed logging for static files to improve performance
        is_static = request.url.path.startswith(('/static/', '/saas/'))
        
        if is_static:
            # Fast path for static files - no logging
            return await call_next(request)
        
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
app.include_router(additional_router, prefix="/api", tags=["additional"])
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
    Lightweight health check for Azure load balancers and monitoring.
    
    Returns:
        Basic health status
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with agent testing (for manual testing only).
    WARNING: This endpoint is resource-intensive and should not be used for automated health checks.
    
    Returns:
        Health status including agent functionality test
    """
    # Check if real agents are available by verifying required environment variables
    real_agents_available = bool(
        os.getenv("TAVILY_API_KEY") and 
        os.getenv("GOOGLE_API_KEY") and 
        os.getenv("LLM_MODEL")
    )
    
    # Test agent functionality
    agent_test_result = {
        "test_performed": False,
        "using_real_agent": False,
        "response_preview": None,
        "error": None
    }
    
    try:
        # Import required modules for agent testing
        from app.db.session import get_db
        from app.agents.agent_factory import get_agent_factory
        import uuid
        
        # Create a test database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Create agent factory (no organization_id for health check)
            agent_factory = get_agent_factory(db=db, organization_id=None)
            
            # Create a test conversation ID
            test_conversation_id = f"health_check_{uuid.uuid4()}"
            
            # Create coordinator agent
            agent = agent_factory.create_agent(
                agent_type="coordinator",
                conversation_id=test_conversation_id
            )
            
            # Add a simple test message
            state = agent["state"]
            if "messages" not in state:
                state["messages"] = []
            
            test_message = {
                "role": "user",
                "content": "Hello, this is a health check test.",
                "timestamp": time.time()
            }
            state["messages"].append(test_message)
            
            # Run the agent graph
            result = agent["graph"].invoke(state)
            
            # Extract the response
            assistant_messages = [
                msg for msg in result.get("messages", [])
                if msg.get("role") == "assistant" and not msg.get("ephemeral", False)
            ]
            
            if assistant_messages:
                response = assistant_messages[-1]["content"]
                
                # Check if response indicates mock or real agent
                is_mock = (
                    "mock response" in response.lower() or
                    "this is a mock" in response.lower() or
                    "mock" in response.lower()
                )
                
                agent_test_result.update({
                    "test_performed": True,
                    "using_real_agent": not is_mock,
                    "response_preview": response[:100] + "..." if len(response) > 100 else response,
                    "error": None
                })
            else:
                agent_test_result.update({
                    "test_performed": True,
                    "using_real_agent": False,
                    "response_preview": "No response received",
                    "error": "No assistant response found"
                })
                
            # Clean up test conversation
            try:
                agent_factory.state_manager.delete_conversation(test_conversation_id)
            except:
                pass  # Ignore cleanup errors
                
        except Exception as agent_error:
            agent_test_result.update({
                "test_performed": True,
                "using_real_agent": False,
                "response_preview": None,
                "error": str(agent_error)
            })
        finally:
            # Close database session
            try:
                db.close()
            except:
                pass
                
    except Exception as test_error:
        agent_test_result.update({
            "test_performed": False,
            "using_real_agent": False,
            "response_preview": None,
            "error": f"Test setup failed: {str(test_error)}"
        })
    
    return {
        "status": "healthy",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "real_agents_available": real_agents_available,
        "agent_test": agent_test_result,
        "use_real_agents": os.getenv("USE_REAL_AGENTS", "false").lower() == "true"
    }


@app.get("/debug/env")
async def debug_env():
    """
    Debug endpoint to check environment variables.
    
    Returns:
        Environment variable status
    """
    tavily_key = os.getenv("TAVILY_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    llm_model = os.getenv("LLM_MODEL")
    
    return {
        "tavily_key_present": bool(tavily_key),
        "tavily_key_length": len(tavily_key) if tavily_key else 0,
        "google_key_present": bool(google_key),
        "google_key_length": len(google_key) if google_key else 0,
        "llm_model_present": bool(llm_model),
        "llm_model_value": llm_model,
        "real_agents_available": bool(tavily_key and google_key and llm_model),
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8002"))
    
    uvicorn.run("app.main_saas:app", host=host, port=port, reload=True)
