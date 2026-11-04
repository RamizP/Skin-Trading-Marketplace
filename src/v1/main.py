import uvicorn
from fastapi import APIRouter, FastAPI

from auth.router import app as auth_router
from entity.router import app as entity_router
from inventory.router import app as inventory_router
from order.router import app as order_router
from case.router import app as case_router

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
app.include_router(case_router.router, prefix="", tags=["Case"])

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
    uvicorn.run("main:app", port=8000, ssl_keyfile="certificates/key.pem", ssl_certfile="certificates/cert.pem")
