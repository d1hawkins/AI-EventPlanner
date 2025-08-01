from fastapi import Request, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.db.models_updated import Organization


async def extract_tenant_id(request: Request) -> Optional[int]:
    """
    Extract tenant ID from request.
    
    Tries to extract tenant ID from:
    1. Header (X-Tenant-ID)
    2. Subdomain
    3. Path parameter
    
    Args:
        request: FastAPI request
        
    Returns:
        Tenant ID or None if not found
    """
    # Try to get from header
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id and tenant_id.isdigit():
        return int(tenant_id)
    
    # Try to get from subdomain
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        if subdomain != "www" and subdomain:
            # Look up organization by slug
            db = request.state.db
            org = db.query(Organization).filter(Organization.slug == subdomain).first()
            if org:
                return org.id
    
    # Try to get from path parameter
    if "organization_id" in request.path_params:
        org_id = request.path_params["organization_id"]
        if isinstance(org_id, int) or (isinstance(org_id, str) and org_id.isdigit()):
            return int(org_id)
    
    return None


async def tenant_middleware(request: Request, call_next):
    """
    Middleware to extract tenant ID and set it in request state.
    
    Args:
        request: FastAPI request
        call_next: Next middleware or route handler
        
    Returns:
        Response
    """
    # Skip database operations for health check requests
    if request.url.path == "/health":
        return await call_next(request)
    
    try:
        # Get DB session
        db = next(get_db())
        request.state.db = db
        
        # Extract tenant ID
        tenant_id = await extract_tenant_id(request)
        request.state.tenant_id = tenant_id
    except Exception as e:
        # Log the error but continue with the request
        print(f"Error in tenant middleware: {e}")
        # If this is a health check or static file, continue without the database
        if request.url.path.startswith("/static") or request.url.path.startswith("/saas"):
            pass
        else:
            # For API requests, we might want to return an error
            # But for now, let's just continue and let the route handler handle it
            pass
    
    # Continue with request
    response = await call_next(request)
    
    return response


def get_tenant_id(request: Request) -> Optional[int]:
    """
    Get tenant ID from request state.
    
    Args:
        request: FastAPI request
        
    Returns:
        Tenant ID or None if not found
    """
    try:
        # Check if request has state attribute (MockRequest might not have it)
        if hasattr(request, 'state'):
            return getattr(request.state, "tenant_id", None)
        else:
            # For MockRequest or other request objects without state
            return None
    except AttributeError:
        # Fallback for any attribute errors
        return None


def require_tenant(request: Request) -> int:
    """
    Require tenant ID to be present in request state.
    
    Args:
        request: FastAPI request
        
    Returns:
        Tenant ID
        
    Raises:
        HTTPException: If tenant ID is not found
    """
    tenant_id = get_tenant_id(request)
    if tenant_id is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID is required"
        )
    return tenant_id


def get_current_organization(request: Request, db: Session = Depends(get_db)) -> Optional[Organization]:
    """
    Get current organization from request state.
    
    Args:
        request: FastAPI request
        db: Database session
        
    Returns:
        Organization object or None if not found
    """
    tenant_id = get_tenant_id(request)
    if tenant_id is None:
        return None
    
    try:
        return db.query(Organization).filter(Organization.id == tenant_id).first()
    except Exception as e:
        print(f"Error getting current organization: {e}")
        return None
