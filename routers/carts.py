import os
from typing import Any, Dict, List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from database import get_supabase_client

router = APIRouter(prefix="/carts", tags=["Carts"])
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "secreto_desarrollo")
ALGORITHM = "HS256"


class CartProductItem(BaseModel):
    productId: int
    quantity: int


class CartCreate(BaseModel):
    # El userId se toma del token JWT, no del cuerpo de la petición.
    date: str
    products: List[CartProductItem]


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """Valida el JWT y devuelve el ID del usuario autenticado."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return int(payload.get("sub"))
    except (jwt.PyJWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )


def _to_cart_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row.get("id"),
        "userId": row.get("user_id"),
        "date": row.get("date"),
        "products": row.get("products") or [],
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_cart(
    cart: CartCreate,
    user_id: int = Depends(get_current_user_id),
) -> Dict[str, Any]:
    """Registra un carrito (compra) del usuario autenticado."""
    if not cart.products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El carrito no tiene productos",
        )
    if any(item.quantity <= 0 for item in cart.products):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las cantidades deben ser mayores a cero",
        )

    supabase = get_supabase_client()
    result = (
        supabase.table("carts")
        .insert(
            {
                "user_id": user_id,
                "date": cart.date,
                "products": [item.model_dump() for item in cart.products],
            }
        )
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo registrar el carrito",
        )
    return _to_cart_dict(result.data[0])


@router.get("")
def get_my_carts(user_id: int = Depends(get_current_user_id)) -> List[Dict[str, Any]]:
    """Devuelve el historial de carritos del usuario autenticado."""
    supabase = get_supabase_client()
    result = (
        supabase.table("carts")
        .select("id, user_id, date, products")
        .eq("user_id", user_id)
        .order("date", desc=True)
        .execute()
    )
    return [_to_cart_dict(row) for row in result.data]
