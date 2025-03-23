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
    # Get DB session
    db = next(get_db())
    request.state.db = db
    
    # Extract tenant ID
    tenant_id = await extract_tenant_id(request)
    request.state.tenant_id = tenant_id
    
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
    return getattr(request.state, "tenant_id", None)


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
