from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
import jwt

app = FastAPI(title="MovieReviews FastAPI Backend")

SECRET_KEY = "secreto_desarrollo"
ALGORITHM = "HS256"

# -------------------------
# MODELOS DE DATOS
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
    id: int
    title: str
    price: float
    description: str
    category: str
    image: str
    rating: Rating

# -------------------------
# BASE DE DATOS EN MEMORIA
# -------------------------

PRODUCTS_DB: List[Product] = [
    Product(
        id=1,
        title="Fjallraven - Foldsack No. 1 Backpack",
        price=109.95,
        description="Your perfect pack for everyday use and walks in the forest.",
        category="men's clothing",
        image="https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
        rating=Rating(rate=3.9, count=120)
    ),
    Product(
        id=2,
        title="Mens Casual Premium Slim Fit T-Shirts",
        price=22.3,
        description="Slim-fit style, contrast raglan long sleeve, three-button henley placket.",
        category="men's clothing",
        image="https://fakestoreapi.com/img/71-3HjGNDUL._AC_SY879._SX._UX._SY._UY_.jpg",
        rating=Rating(rate=4.1, count=259)
    ),
    Product(
        id=3,
        title="John Hardy Women's Legends Naga Gold & Silver Dragon Station Chain Bracelet",
        price=695.0,
        description="From the Legends Collection, the Naga was inspired by the mythical water dragon.",
        category="jewelery",
        image="https://fakestoreapi.com/img/71pWzhdJNwL._AC_UL640_QL65_ML3_.jpg",
        rating=Rating(rate=4.6, count=400)
    )
]

# -------------------------
# ENDPOINTS
# -------------------------

@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    # Base de datos de usuarios de prueba
    # ID 1 o 2 = Administrador, ID 3 = Auditor, otros = Cliente
    users_db = {
        "admin": {"password": "123", "id": 1},
        "auditor": {"password": "123", "id": 3},
        "user": {"password": "123", "id": 5}
    }

    user = users_db.get(request.usuario)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos"
        )

    # El token incluye la clave 'sub' requerida por la app para obtener el ID
    payload = {"sub": user["id"]}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return LoginResponse(token=token)

@app.get("/products", response_model=List[Product])
def get_products():
    return PRODUCTS_DB

@app.get("/products/categories", response_model=List[str])
def get_categories():
    return list(set(p.category for p in PRODUCTS_DB))

@app.get("/products/category/{category}", response_model=List[Product])
def get_products_by_category(category: str):
    return [p for p in PRODUCTS_DB if p.category.lower() == category.lower()]

@app.get("/products/{id}", response_model=Product)
def get_product(id: int):
    for product in PRODUCTS_DB:
        if product.id == id:
            return product
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.put("/products/{id}", response_model=Product)
def update_product(id: int, updated: Product):
    for i, product in enumerate(PRODUCTS_DB):
        if product.id == id:
            PRODUCTS_DB[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.delete("/products/{id}", response_model=Product)
def delete_product(id: int):
    for i, product in enumerate(PRODUCTS_DB):
        if product.id == id:
            return PRODUCTS_DB.pop(i)
    raise HTTPException(status_code=404, detail="Producto no encontrado")