import os
from datetime import datetime, UTC, timedelta

import bcrypt
import jwt
from sqlalchemy.orm import Session

from .. import db

# TODO: IMPORTANT CHANGE EXPIRATION TIME BACK TO MINUTES/DAYS AFTER TESTING!!!!!

# ==================== CONFIG ====================
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 1
# ================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt algorithm"""
    as_bytes = password.encode('utf-8')
    bcrypt.hashpw(as_bytes, bcrypt.gensalt())
    return as_bytes.decode('utf-8')

def check_password(hashed_password: str, password: str) -> bool:
    """Verify password using bcrypt algorithm"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(db_session: Session, data: dict) -> str:
    """Create a new jwt access token."""
    to_encode = data.copy()
    expires_at = datetime.now(UTC) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires_at})

    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    db.add_refresh_token(db_session, token=encoded, user_id=to_encode['sub'], expires_at=expires_at)
    return encoded

def create_refresh_token(data: dict) -> str:
    """Create a new jwt refresh token."""
    to_encode = data.copy()
    expire_time = datetime.now(UTC) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire_time})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

