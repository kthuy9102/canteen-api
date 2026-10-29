from fastapi import FastAPI
from app.routers import categories, menu, orders
 
app = FastAPI(title="Canteen API", version="2.0.0",
              description="API căng tin trường – dữ liệu lưu trong PostgreSQL")
app.include_router(categories.router)
app.include_router(menu.router)
app.include_router(orders.router)
 
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
