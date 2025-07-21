"""Security utilities for AutoVPN."""

import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from autovpn.core.config import settings

# Try to use bcrypt, fallback to sha256 if bcrypt fails
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    USE_BCRYPT = True
except Exception:
    # Fallback to simple hashing if bcrypt fails
    USE_BCRYPT = False


def hash_password(password: str) -> str:
    """Hash a password using bcrypt or sha256 fallback."""
    if USE_BCRYPT:
        return pwd_context.hash(password)
    else:
        # Fallback to sha256 with salt
        salt = os.urandom(16).hex()
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        return f"{salt}${hash_obj.hexdigest()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if USE_BCRYPT:
        return pwd_context.verify(plain_password, hashed_password)
    else:
        # Fallback verification
        try:
            salt, hash_value = hashed_password.split("$", 1)
            hash_obj = hashlib.sha256()
            hash_obj.update((plain_password + salt).encode())
            return hash_obj.hexdigest() == hash_value
        except:
            return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(token: str):
    """Verify a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None
