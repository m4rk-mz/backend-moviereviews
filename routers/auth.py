import os
from fastapi import APIRouter, HTTPException, status
import jwt
from models import LoginRequest, LoginResponse
from database import get_supabase_client

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.environ.get("SECRET_KEY", "secreto_desarrollo")
ALGORITHM = "HS256"

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    supabase = get_supabase_client()
    res = supabase.table("users").select("*").eq("usuario", request.usuario).execute()
    users = res.data

    if not users or users[0]["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos"
        )

    user = users[0]
    payload = {"sub": user["id"]}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return LoginResponse(token=token)