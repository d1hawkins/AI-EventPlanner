from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.session import get_db
from app.db.models import User
from app.schemas.user import User as UserSchema, UserCreate, Token
from app.auth.dependencies import create_access_token, get_current_user

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Bcrypt has a 72-byte limit, truncate password if needed (must match hash function)
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        plain_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    # Bcrypt has a 72-byte limit, truncate password if needed
    # This is a safe operation as bcrypt security doesn't benefit from passwords > 72 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> User:
    """Authenticate a user by username or email and password."""
    # Try to find user by username first, then by email
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = db.query(User).filter(User.email == username).first()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/register", response_model=UserSchema)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Register a new user with tenant-aware setup.
    
    Args:
        user_in: User data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If user already exists
    """
    # Check if user already exists
    user = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    
    # Create new user
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
    )
    db.add(db_user)
    db.flush()  # Flush to get the user ID
    
    # Create organization for the user (personal organization)
    from app.db.models_saas import Organization, OrganizationUser
    import uuid
    
    organization = Organization(
        name=f"{user_in.username}'s Organization",
        slug=f"{user_in.username.lower()}-{uuid.uuid4().hex[:8]}",
        plan_id="free"
    )
    db.add(organization)
    db.flush()  # Flush to get the organization ID
    
    # Create organization-user relationship
    org_user = OrganizationUser(
        organization_id=organization.id,
        user_id=db_user.id,
        role="admin",
        is_primary=True
    )
    db.add(org_user)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        db: Database session
        form_data: Form data with username and password
        
    Returns:
        Access token
        
    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user
    """
    return current_user


@router.get("/me/organization")
def get_user_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get the current user's primary organization.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Organization information
    """
    from app.db.models_saas import OrganizationUser
    
    # Get user's primary organization
    org_user = db.query(OrganizationUser).filter(
        OrganizationUser.user_id == current_user.id,
        OrganizationUser.is_primary == True
    ).first()
    
    if not org_user:
        # If no primary organization, get any organization
        org_user = db.query(OrganizationUser).filter(
            OrganizationUser.user_id == current_user.id
        ).first()
    
    if not org_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no organization",
        )
    
    return {
        "organization_id": org_user.organization_id,
        "role": org_user.role
    }
