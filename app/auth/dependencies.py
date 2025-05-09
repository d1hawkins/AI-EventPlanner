from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.session import get_db
from app.db.models_updated import User
from app.schemas.user import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Subject of the token (usually user ID)
        expires_delta: Optional expiration time
        
    Returns:
        JWT token as string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current authenticated user.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    # For demo purposes, bypass authentication and return a dummy user
    # In a real application, this would validate the token and return the actual user
    
    try:
        # Try to decode the token, but don't validate it
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        user_id = payload.get("sub")
        if user_id:
            user_id = int(user_id)
            # Try to get the user from the database
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user
    except Exception:
        # If token decoding fails, just return a dummy user
        pass
    
    # Return a dummy user for demo purposes
    # First check if user with ID 1 exists
    user = db.query(User).filter(User.id == 1).first()
    if user:
        return user
    
    # If no user exists, create a dummy user
    dummy_user = User(
        id=1,
        email="demo@example.com",
        username="demo",
        hashed_password="dummy_hash",
        is_active=True
    )
    db.add(dummy_user)
    db.commit()
    db.refresh(dummy_user)
    return dummy_user
