"""Security utilities for AutoVPN."""

import hashlib
import os
from passlib.context import CryptContext

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
