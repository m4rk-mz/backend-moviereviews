from pydantic import BaseModel
from typing import Optional

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