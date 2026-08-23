from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    ai,
    alerts,
    audit,
    auth,
    bootstrap,
    documents,
    evaluation_router,
    integrations,
    meetings,
    metrics,
    policies,
    projects,
    security_router,
    simulation,
    tasks,
    users,
    ws,
)
from app.services.realtime import manager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await manager.startup()
    yield
    await manager.shutdown()


app = FastAPI(
    title="Nexus Mind Enterprise API",
    description="AI-Powered Engineering Operations Platform API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(meetings.router)
app.include_router(policies.router)
app.include_router(alerts.router)
app.include_router(ai.router)
app.include_router(bootstrap.router)
app.include_router(ws.router)

# Enterprise AI, RAG, ML, Security & Integration Routers
app.include_router(documents.router)
app.include_router(simulation.router)
app.include_router(security_router.router)
app.include_router(audit.router)
app.include_router(integrations.router)
app.include_router(metrics.router)
app.include_router(evaluation_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "platform": "Nexus Mind Enterprise", "version": "2.0.0"}


# Serve Production Web Build (Unified Single-Port Deployment)
import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

web_dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web", "dist")
if os.path.exists(web_dist_path):
    assets_dir = os.path.join(web_dist_path, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa_frontend(full_path: str):
        if full_path.startswith("api") or full_path.startswith("ws") or full_path.startswith("metrics") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = os.path.join(web_dist_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(web_dist_path, "index.html"))

