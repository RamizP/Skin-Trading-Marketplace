# main.py
import uvicorn
from fastapi import FastAPI

from auth.router import app as auth_router
from entity.router import app as entity_router
from balance.router import app as balance_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trading Engine")
origins = [
    "*"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies allowed origins
    allow_credentials=True,  # Allow cookies to be sent
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth_router.router, prefix="", tags=["Auth"])
app.include_router(entity_router.router, prefix="", tags=["Entity"])
app.include_router(balance_router.router, prefix="", tags=["Balance"])