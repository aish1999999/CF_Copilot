"""
Authentication and authorization using OAuth 2.0 and JWT.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    email: Optional[str] = None


class User(BaseModel):
    """User model."""
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get current authenticated user from token.

    Args:
        token: JWT access token

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    # In production, fetch user from database
    # For now, return a mock user
    user = User(
        username=token_data.username,
        email=f"{token_data.username}@example.com"
    )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (not disabled).

    Args:
        current_user: Current user from token

    Returns:
        Active user

    Raises:
        HTTPException: If user is disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate user with username and password.

    Args:
        username: Username
        password: Password

    Returns:
        User if authenticated, None otherwise
    """
    # In production, fetch user from database
    # For now, use a mock user database
    fake_users_db = {
        "testuser": {
            "username": "testuser",
            "full_name": "Test User",
            "email": "testuser@example.com",
            "hashed_password": get_password_hash("testpass"),
            "disabled": False,
        }
    }

    user_dict = fake_users_db.get(username)

    if not user_dict:
        return None

    user = UserInDB(**user_dict)

    if not verify_password(password, user.hashed_password):
        return None

    return user


# OAuth2 providers configuration
class OAuthProvider(BaseModel):
    """OAuth provider configuration."""
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    redirect_uri: str


# Google OAuth configuration
GOOGLE_OAUTH = OAuthProvider(
    client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    token_url="https://oauth2.googleapis.com/token",
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
)


def get_google_oauth_url() -> str:
    """
    Get Google OAuth authorization URL.

    Returns:
        Authorization URL
    """
    from urllib.parse import urlencode

    params = {
        "client_id": GOOGLE_OAUTH.client_id,
        "redirect_uri": GOOGLE_OAUTH.redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }

    return f"{GOOGLE_OAUTH.authorize_url}?{urlencode(params)}"
