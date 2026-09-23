import sys
import os

# Dynamically find the exact paths for backend and services
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.outfits import router as outfits_router
from routes.auth import router as auth_router

app = FastAPI(title="Mein API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this up before production!
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(outfits_router)
app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "mein-api"}