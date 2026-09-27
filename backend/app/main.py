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
    import logging
    import time
    from sqlalchemy import inspect, text
    from app import models
    from app.database import Base, engine

    logger = logging.getLogger("nexusmind.startup")

    # Connect with retries to tolerate cloud database cold-starts and DNS propagation
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database schema verified/created successfully.")
            break
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"Critical: Database connection failed after {max_retries} attempts: {e}")
                raise
            wait_time = attempt * 2
            logger.warning(
                f"Database connection attempt {attempt}/{max_retries} failed ({e}). "
                f"Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)

    try:
        inspector = inspect(engine)
        if "alerts" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("alerts")]
            if "org_id" not in columns:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE alerts ADD COLUMN org_id VARCHAR(36)"))
                    conn.commit()
    except Exception as e:
        print(f"Warning: Schema alignment check: {e}")

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
@app.get("/health")
def health():
    return {"status": "ok", "platform": "Nexus Mind Enterprise", "version": "2.0.0"}


# Serve Production Web Build (Unified Single-Port Deployment)
import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


def find_web_dist_path() -> str | None:
    candidates = [
        os.environ.get("FRONTEND_DIST_DIR"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web", "dist"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "dist"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "dist"),
        os.path.join(os.getcwd(), "web", "dist"),
        os.path.join(os.getcwd(), "dist"),
    ]
    for p in candidates:
        if p and os.path.exists(p) and os.path.isdir(p):
            index_file = os.path.join(p, "index.html")
            if os.path.exists(index_file):
                return os.path.abspath(p)
    return None


web_dist_path = find_web_dist_path()
if web_dist_path:
    assets_dir = os.path.join(web_dist_path, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa_frontend(full_path: str):
        if (
            full_path.startswith("api")
            or full_path.startswith("ws")
            or full_path.startswith("metrics")
            or full_path.startswith("docs")
            or full_path.startswith("openapi.json")
            or full_path.startswith("redoc")
            or full_path == "health"
        ):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = os.path.join(web_dist_path, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(web_dist_path, "index.html"))



if __name__ == "__main__":
    import uvicorn
    cfg = get_settings()
    server_port = int(os.environ.get("PORT", cfg.port))
    server_host = os.environ.get("HOST", cfg.host)
    uvicorn.run("app.main:app", host=server_host, port=server_port, reload=False)


