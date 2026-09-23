from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import auth_services, db_services

router = APIRouter(tags=["auth"])


class SignupRequest(BaseModel):
    email: str
    password: str
    campus: Optional[str] = None
    display_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/auth/signup")
def signup(request: SignupRequest):
    try:
        result = auth_services.sign_up(request.email, request.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if result.user is None or result.session is None:
        raise HTTPException(
            status_code=400,
            detail="Signup requires email confirmation before a session is issued",
        )

    db_services.supabase.table("profiles").insert({
        "id": result.user.id,
        "campus": request.campus,
        "display_name": request.display_name,
    }).execute()

    return {"user_id": result.user.id, "token": result.session.access_token}


@router.post("/auth/login")
def login(request: LoginRequest):
    try:
        result = auth_services.sign_in(request.email, request.password)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"user_id": result.user.id, "token": result.session.access_token}
