import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from auth.router import router as auth_router
from case.router import router as case_router
from database import SessionLocal
from demo import initialize_demo_data
from entity.router import router as entity_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from inventory.router import router as inventory_router
from order.router import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("DEMO_DATA", "true").strip().casefold() not in {
        "false",
        "0",
        "no",
        "off",
    }:
        with SessionLocal() as db:
            initialize_demo_data(db)
    yield


app = FastAPI(title="Trading Engine", lifespan=lifespan)

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


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(entity_router)
app.include_router(inventory_router)
app.include_router(order_router)
app.include_router(case_router)

# The container includes a frontend build; local development uses Vite.
# Register this last so API routes take priority over static files.
frontend = Path(__file__).resolve().parents[2] / "frontend"
if frontend.is_dir():
    app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
    uvicorn.run(
        "main:app",
        port=8000,
        ssl_keyfile="certificates/key.pem",
        ssl_certfile="certificates/cert.pem",
    )
