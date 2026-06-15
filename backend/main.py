import sys
import os

# 1. Dynamically find the exact paths for backend and services
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

# 2. Use a direct, explicit fallback import that VS Code cannot miss
try:
    from services.gemini_services import analyse_outfit
except ModuleNotFoundError:
    import gemini_services as services
    analyse_outfit = services.analyse_outfit

app = FastAPI(title="Mein API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this up before production!
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyseRequest(BaseModel):
    user_id: str
    image_url: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "mein-api"}

@app.post("/analyse-outfit")
async def analyse_outfit_route(request: AnalyseRequest):
    try:
        result = await analyse_outfit(request.image_url)
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON structure")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))