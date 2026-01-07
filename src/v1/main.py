# main.py
import uvicorn
from fastapi import APIRouter, FastAPI

from auth.router import app as auth_router
from entity.router import app as entity_router
from inventory.router import app as inventory_router
from order.router import app as order_router

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trading Engine")

origins = [
    "http://localhost:5173",
    "https://localhost:5173",
]

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

if __name__ == "__main__":
     uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
    # uvicorn.run(app, port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")