import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import jwt
from supabase import create_client, Client

app = FastAPI(title="MovieReviews FastAPI + Supabase")

# -------------------------
# CONFIGURACIÓN DE VARIABLES DE ENTORNO
# -------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://hubnsnszeubcpyvykfnf.supabase.co/rest/v1/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_secret_vJM2Ga63PwPSnpiQkJ_iSg_J9y9wCvP")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

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
# HELPER DE VERIFICACIÓN
# -------------------------
def check_supabase():
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Variables de entorno SUPABASE_URL o SUPABASE_KEY no configuradas en Render"
        )

# -------------------------
# ENDPOINTS CON SUPABASE
# -------------------------

@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    check_supabase()
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
    check_supabase()
    res = supabase.table("products").select("*").execute()
    products = []
    for item in res.data:
        products.append(Product(
            id=item["id"],
            title=item["title"],
            price=float(item["price"]),
            description=item["description"] or "",
            category=item["category"],
            image=item["image"] or "",
            rating=Rating(rate=float(item.get("rate", 0)), count=int(item.get("count", 0)))
        ))
    return products

@app.get("/products/categories", response_model=List[str])
def get_categories():
    check_supabase()
    res = supabase.table("products").select("category").execute()
    categories = list(set(item["category"] for item in res.data if item.get("category")))
    return categories

@app.get("/products/category/{category}", response_model=List[Product])
def get_products_by_category(category: str):
    check_supabase()
    res = supabase.table("products").select("*").ilike("category", category).execute()
    products = []
    for item in res.data:
        products.append(Product(
            id=item["id"],
            title=item["title"],
            price=float(item["price"]),
            description=item["description"] or "",
            category=item["category"],
            image=item["image"] or "",
            rating=Rating(rate=float(item.get("rate", 0)), count=int(item.get("count", 0)))
        ))
    return products

@app.get("/products/{id}", response_model=Product)
def get_product(id: int):
    check_supabase()
    res = supabase.table("products").select("*").eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    item = res.data[0]
    return Product(
        id=item["id"],
        title=item["title"],
        price=float(item["price"]),
        description=item["description"] or "",
        category=item["category"],
        image=item["image"] or "",
        rating=Rating(rate=float(item.get("rate", 0)), count=int(item.get("count", 0)))
    )

@app.put("/products/{id}", response_model=Product)
def update_product(id: int, updated: Product):
    check_supabase()
    update_data = {
        "title": updated.title,
        "price": updated.price,
        "description": updated.description,
        "category": updated.category,
        "image": updated.image,
        "rate": updated.rating.rate,
        "count": updated.rating.count
    }
    res = supabase.table("products").update(update_data).eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return updated

@app.delete("/products/{id}", response_model=Product)
def delete_product(id: int):
    check_supabase()
    res_get = supabase.table("products").select("*").eq("id", id).execute()
    if not res_get.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    deleted_item = res_get.data[0]
    supabase.table("products").delete().eq("id", id).execute()
    
    return Product(
        id=deleted_item["id"],
        title=deleted_item["title"],
        price=float(deleted_item["price"]),
        description=deleted_item["description"] or "",
        category=deleted_item["category"],
        image=deleted_item["image"] or "",
        rating=Rating(rate=float(deleted_item.get("rate", 0)), count=int(deleted_item.get("count", 0)))
    )
