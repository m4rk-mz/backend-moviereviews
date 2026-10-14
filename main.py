@app.get("/products", response_model=List[Product])
def get_products():
    check_supabase()
    res = supabase.table("products").select("*").execute()
    products = []
    for item in res.data:
        # Extraer rating si viene como objeto JSON o como columnas separadas
        rating_data = item.get("rating") or {}
        rate_val = rating_data.get("rate") if isinstance(rating_data, dict) else item.get("rate", 0)
        count_val = rating_data.get("count") if isinstance(rating_data, dict) else item.get("count", 0)

        products.append(Product(
            id=item.get("id"),
            title=item.get("title", ""),
            price=float(item.get("price") or 0.0),
            description=item.get("description") or "",
            category=item.get("category", ""),
            image=item.get("image") or "",
            rating=Rating(rate=float(rate_val or 0.0), count=int(count_val or 0))
        ))
    return products
