import os
from datetime import datetime, UTC

import bcrypt
import jwt
from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from sqlalchemy.orm import Session

from .schemas import *
from . import utils
from .. import db as database


router = APIRouter()




# ==================== GET ====================



# ==================== POST ====================

@router.post("/register")
def register_user(rf: RegisterForm, db: Session = Depends(database.get_db)):
    """Register a user"""
    hashed_password = bcrypt.hashpw(rf.password.encode("utf-8"), bcrypt.gensalt())

    database.create_user(
        db=db,
        email=rf.email,
        username=rf.username,
        hashed_password=hashed_password.decode("utf-8"),
    )


@router.post("/login")
def login_user(lf: LoginForm, response: Response, db: Session = Depends(database.get_db)):
    user = database.get_user_by_username(db=db, username=lf.username)
    if not user or not utils.check_password(hashed_password=user.hashed_password, password=lf.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    data = {"sub": str(user.id)}
    at = utils.create_access_token(data)
    rt = utils.create_refresh_token(db, data)

    response.set_cookie(key="refresh_token", value=rt, httponly=True, path="/auth/refresh")

    return {
        "access_token": at,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    db: Session = Depends(database.get_db),
    refresh_token: str | None = Cookie(default=None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    try:
        payload = jwt.decode(refresh_token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token is expired or invalid")

    stored = database.get_refresh_token_by_token(db, token=refresh_token)
    if not stored:
        raise HTTPException(status_code=401, detail="Refresh token is expired or invalid")

    access_token = utils.create_access_token({"sub": str(user_id)})
    user = database.get_user_by_id(db=db, user_id=user_id)

    return {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }

@router.post("/logout")
def logout_user(logout: LogoutSchema, db: Session = Depends(database.get_db)):
    database.revoke_refresh_token(db, token=logout.refresh_token)
    return {"message": "You have been logged out"}
