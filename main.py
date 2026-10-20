from fastapi import FastAPI
from routers import auth, products

app = FastAPI(title="MovieReviews FastAPI + Supabase Modular")

# Registrar los enrutadores modulares
app.include_router(auth.router)
app.include_router(products.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "API modular funcionando correctamente"}
