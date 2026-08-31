import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from logging_config import configure_logging
from fastapi.middleware.cors import CORSMiddleware
from paths import BASE_DIR, STATIC_DIR
from routes.v1 import api as v1_api
from routes.v1 import audit, evaluation, pages, reviews, settings, transactions

logger = configure_logging()


def create_app() -> FastAPI:
    app = FastAPI(title="ai-risk-manager")
    app.state.logger = logger
    logger.info("Starting AI Risk Manager application")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_api.router)
    app.include_router(pages.router)
    app.include_router(transactions.router)
    app.include_router(reviews.router)
    app.include_router(evaluation.router)
    app.include_router(audit.router)
    app.include_router(settings.router)

    frontend_dist = BASE_DIR / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

        @app.get("/app", response_class=HTMLResponse)
        async def serve_react_app():
            return (frontend_dist / "index.html").read_text(encoding="utf-8")

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app


app = create_app()


def run() -> None:
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
