from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from .database import engine
from . import models
from .  import products, customers, orders

# Create all tables on startup (use Alembic in production)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory & Order Management API",
    description="Product, Customer, and Order management with inventory tracking",
    version="1.0.0"
)

# CORS — adjust origins for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global handler for unexpected DB integrity errors
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "A unique constraint was violated. Check for duplicate SKU or email."}
    )

# Register routers
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Inventory & Order Management API is running"}
