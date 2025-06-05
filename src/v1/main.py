# main.py
import uvicorn
from fastapi import FastAPI

from auth.router import app as auth_router
from entity.router import app as entity_router
from inventory.router import app as inventory_router
from order.router import app as order_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trading Engine")
origins = [
    "https://car3.rpashaiev.ddev.site",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="", tags=["Auth"])
app.include_router(entity_router.router, prefix="", tags=["Entity"])
app.include_router(inventory_router.router, prefix="", tags=["Inventory"])
app.include_router(order_router.router, prefix="", tags=["Order"])