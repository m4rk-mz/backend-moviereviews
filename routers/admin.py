import os
from typing import Any, Dict, List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import get_supabase_client

router = APIRouter(tags=["Admin"])
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "secreto_desarrollo")
ALGORITHM = "HS256"


def verify_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """Valida el JWT y comprueba que el usuario autenticado sea admin."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id = int(payload.get("sub"))
    except (jwt.PyJWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    supabase = get_supabase_client()
    result = (
        supabase.table("users")
        .select("id, usuario")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )

    if not result.data or str(result.data[0].get("usuario", "")).lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador",
        )

    return user_id


@router.get("/users")
def get_users(_: int = Depends(verify_admin)) -> List[Dict[str, Any]]:
    """Devuelve usuarios sin exponer contraseñas."""
    supabase = get_supabase_client()
    result = (
        supabase.table("users")
        .select("id, usuario, email")
        .order("id")
        .execute()
    )

    return [
        {
            "id": user.get("id"),
            "usuario": user.get("usuario"),
            "username": user.get("usuario"),
            "email": user.get("email"),
        }
        for user in result.data
    ]


@router.get("/carts")
def get_carts(_: int = Depends(verify_admin)) -> List[Dict[str, Any]]:
    """Devuelve el historial de carritos para el panel de administración."""
    supabase = get_supabase_client()
    result = (
        supabase.table("carts")
        .select("id, user_id, date, products")
        .order("date", desc=True)
        .execute()
    )

    return [
        {
            "id": cart.get("id"),
            "userId": cart.get("user_id"),
            "date": cart.get("date"),
            "products": cart.get("products") or [],
        }
        for cart in result.data
    ]
