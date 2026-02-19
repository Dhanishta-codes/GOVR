from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
import os

from agent.core.graph import run_sdr_agent
import agent.infra.config as config

app = FastAPI(
    title="GOVR — Governed Revenue Execution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"tryItOutEnabled": True}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunRequest(BaseModel):
    company_name: str

@app.get("/health")
def health():
    return {
        "status": "operational",
        "provider": config.AI_PROVIDER,
        "model": config.MODELS.get(config.AI_PROVIDER)
    }

@app.post("/api/run")
async def run_agent(request: RunRequest):
    company_name = request.company_name.strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="company_name is required")
    try:
        final_state = run_sdr_agent(company_name)
        return JSONResponse(content=dict(final_state))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend LAST
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")