from fastapi import APIRouter, HTTPException
from typing import List
from models import Product, Rating
from database import get_supabase_client

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[Product])
def get_products():
    supabase = get_supabase_client()
    res = supabase.table("products").select("*").execute()
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
            rating=Rating(rate=float(r_rate or 0.0), count=int(r_count or 0))
        ))
    return products

@router.get("/{id}", response_model=Product)
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

@router.put("/{id}", response_model=Product)
def update_product(id: int, updated: Product):
    supabase = get_supabase_client()
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

@router.delete("/{id}", response_model=Product)
def delete_product(id: int):
    supabase = get_supabase_client()
    res_get = supabase.table("products").select("*").eq("id", id).execute()
    if not res_get.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    deleted_item = res_get.data[0]
    supabase.table("products").delete().eq("id", id).execute()
    
    return Product(
        id=deleted_item["id"],
        title=str(deleted_item.get("title", "")),
        price=float(deleted_item.get("price") or 0.0),
        description=str(deleted_item.get("description") or ""),
        category=str(deleted_item.get("category", "")),
        image=str(deleted_item.get("image") or ""),
        rating=Rating(
            rate=float(deleted_item.get("rate", 0.0) or 0.0),
            count=int(deleted_item.get("count", 0) or 0)
        )
    )