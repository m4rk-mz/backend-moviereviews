import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import jwt
from supabase import create_client, Client

app = FastAPI(title="MovieReviews FastAPI + Supabase")

# -------------------------
# RUTA RAÍZ (HEALTH CHECK)
# -------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "MovieReviews API funcionando correctamente"}

# -------------------------
# CONFIGURACIÓN DE SUPABASE
# -------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Variables SUPABASE_URL o SUPABASE_KEY no configuradas en Render"
        )
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar con Supabase: {str(e)}"
        )

SECRET_KEY = os.environ.get("SECRET_KEY", "secreto_desarrollo")
ALGORITHM = "HS256"

# -------------------------
# MODELOS DE DATOS (PYDANTIC)
# -------------------------
class LoginRequest(BaseModel):
    usuario: str
    password: str

class LoginResponse(BaseModel):
    token: str

class Rating(BaseModel):
    rate: float
    count: int

class Product(BaseModel):
    id: Optional[int] = None
    title: str
    price: float
    description: str
    category: str
    image: str
    rating: Rating

# -------------------------
# ENDPOINTS
# -------------------------

@app.post("/auth/login", response_model=LoginResponse)
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

@app.get("/products", response_model=List[Product])
def get_products():
    supabase = get_supabase_client()
    res = supabase.table("products").select("*").execute()
    products = []
    
    for item in res.data:
        # Extraer rating si viene como objeto dict o desde columnas sueltas
        rating_obj = item.get("rating")
        if isinstance(rating_obj, dict):
            r_rate = rating_obj.get("rate", 0.0)
            r_count = rating_obj.get("count", 0)
        else:
            r_rate = item.get("rate", 0.0)
            r_count = item.get("count", 0)

        products.append(Product(
            id=item.get("id"),
            title=str(item.get("title", "")),
            price=float(item.get("price") or 0.0),
            description=str(item.get("description") or ""),
            category=str(item.get("category", "")),
            image=str(item.get("image") or ""),
            rating=Rating(
                rate=float(r_rate or 0.0),
                count=int(r_count or 0)
            )
        ))
    return products

@app.get("/products/categories", response_model=List[str])
def get_categories():
    supabase = get_supabase_client()
    res = supabase.table("products").select("category").execute()
    categories = list(set(item["category"] for item in res.data if item.get("category")))
    return categories

@app.get("/products/category/{category}", response_model=List[Product])
def get_products_by_category(category: str):
    supabase = get_supabase_client()
    res = supabase.table("products").select("*").ilike("category", category).execute()
    products = []
    for item in res.data:
        rating_obj = item.get("rating")
        if isinstance(rating_obj, dict):
            r_rate = rating_obj.get("rate", 0.0)
            r_count = rating_obj.get("count", 0)
        else:
            r_rate = item.get("rate", 0.0)
            r_count = item.get("count", 0)

        products.append(Product(
            id=item.get("id"),
            title=str(item.get("title", "")),
            price=float(item.get("price") or 0.0),
            description=str(item.get("description") or ""),
            category=str(item.get("category", "")),
            image=str(item.get("image") or ""),
            rating=Rating(
                rate=float(r_rate or 0.0),
                count=int(r_count or 0)
            )
        ))
    return products

@app.get("/products/{id}", response_model=Product)
def get_product(id: int):
    supabase = get_supabase_client()
    res = supabase.table("products").select("*").eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    item = res.data[0]
    rating_obj = item.get("rating")
    if isinstance(rating_obj, dict):
        r_rate = rating_obj.get("rate", 0.0)
        r_count = rating_obj.get("count", 0)
    else:
        r_rate = item.get("rate", 0.0)
        r_count = item.get("count", 0)

    return Product(
        id=item.get("id"),
        title=str(item.get("title", "")),
        price=float(item.get("price") or 0.0),
        description=str(item.get("description") or ""),
        category=str(item.get("category", "")),
        image=str(item.get("image") or ""),
        rating=Rating(
            rate=float(r_rate or 0.0),
            count=int(r_count or 0)
        )
    )
