import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app.database.init_db import init_db
from app.services.data_collector import run_full_data_sync

from app.api.dashboard import router as dashboard_router
from app.api.stations import router as stations_router
from app.api.rivers import router as rivers_router
from app.api.observations import router as observations_router
from app.api.rainfall import router as rainfall_router
from app.api.upstream import router as upstream_router
from app.api.prediction import router as prediction_router
from app.api.alerts import router as alerts_router
from app.api.data_management import router as data_management_router
from app.api.weather import router as weather_router

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
)
logger = logging.getLogger("FloodShield")

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB schema and run initial sync if needed
    logger.info("[FloodShield-AI] Starting up...")
    init_db()

    # Schedule background data synchronization every 30 minutes
    scheduler.add_job(run_full_data_sync, "interval", minutes=30, id="cwc_data_sync", replace_existing=True)
    scheduler.start()
    logger.info("[FloodShield-AI] Background data collector scheduler started (every 30 mins).")

    yield

    # Shutdown
    logger.info("[FloodShield-AI] Shutting down scheduler...")
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="FloodShield-AI API",
    version="2.0.0",
    description="Karnataka-Wide Flood Risk Monitoring and Decision Support System",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routers
app.include_router(dashboard_router, prefix="/api")
app.include_router(stations_router, prefix="/api")
app.include_router(rivers_router, prefix="/api")
app.include_router(observations_router, prefix="/api")
app.include_router(rainfall_router, prefix="/api")
app.include_router(upstream_router, prefix="/api")
app.include_router(prediction_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(data_management_router, prefix="/api")
app.include_router(weather_router, prefix="/api")

# Also mount without /api prefix for backward compatibility
app.include_router(dashboard_router)
app.include_router(stations_router)
app.include_router(rivers_router)
app.include_router(observations_router)
app.include_router(rainfall_router)
app.include_router(upstream_router)
app.include_router(prediction_router)
app.include_router(alerts_router)
app.include_router(data_management_router)


# --- Static Frontend Serving & Health Endpoints ---
DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

@app.get("/health")
def health():
    return {
        "status": "Healthy",
        "system": "FloodShield-AI",
        "scheduler_running": scheduler.running
    }

if os.path.isdir(DIST_DIR) and os.path.exists(os.path.join(DIST_DIR, "index.html")):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(os.path.join(DIST_DIR, "index.html"))

    @app.get("/favicon.svg")
    def serve_favicon():
        fav = os.path.join(DIST_DIR, "favicon.svg")
        if os.path.isfile(fav):
            return FileResponse(fav)
        return FileResponse(os.path.join(DIST_DIR, "index.html"))

    @app.get("/icons.svg")
    def serve_icons():
        icons_path = os.path.join(DIST_DIR, "icons.svg")
        if os.path.isfile(icons_path):
            return FileResponse(icons_path)
        return FileResponse(os.path.join(DIST_DIR, "index.html"))

    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "project": "FloodShield-AI",
            "title": "Karnataka Flood Risk Monitoring and Decision Support System",
            "version": "2.0.0",
            "status": "Operational",
            "docs_url": "/docs"
        }
