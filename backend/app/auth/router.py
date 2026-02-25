import os

import bcrypt
import jwt
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session

from .schemas import *
from . import utils
from .. import db


router = APIRouter()




# ==================== GET ====================



# ==================== POST ====================

@router.post("/register")
def register_user(rf: RegisterForm, db_session: Session = Depends(db.get_db)):
    """Register a user"""
    hashed_password = bcrypt.hashpw(rf.password.encode("utf-8"), bcrypt.gensalt())

    db.create_user(
        db=db_session,
        email=rf.email,
        username=rf.username,
        hashed_password=hashed_password.decode("utf-8"),
    )


@router.post("/login")
def login_user(lf: LoginForm, response: Response, db_session: Session = Depends(db.get_db)):
    user = db.get_user_by_username(db=db_session, username=lf.username)
    if not user or not utils.check_password(hashed_password=user.hashed_password, password=lf.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    data = {"sub": str(user.id)}
    at = utils.create_access_token(data)
    rt = utils.create_refresh_token(db_session, data)

    response.set_cookie(key="refresh_token", value=rt, httponly=True, path="/auth/refresh")

    return {
        "access_token": at,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }


@router.post("/refresh", response_model=Token)
def refresh_token(rt: str, db_session: Session = Depends(db.get_db)):
    try:
        payload = jwt.decode(rt, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token is expired or invalid")

    stored = db.get_refresh_token_by_token(db_session, token=payload["refresh_token"])
    if not stored:
        raise HTTPException(status_code=401, detail="Refresh token is expired or invalid")

    access_token = utils.create_access_token({"sub": str(user_id)})
    return {"access_token": access_token}

@router.post("/logout")
def logout_user(logout: LogoutSchema, db_session: Session = Depends(db.get_db)):
    db.revoke_refresh_token(db_session, token=logout.refresh_token)
    return {"message": "You have been logged out"}
