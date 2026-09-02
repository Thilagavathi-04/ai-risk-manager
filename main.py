import uvicorn
from fastapi import FastAPI

from logging_config import configure_logging
from fastapi.middleware.cors import CORSMiddleware
from routes.v1 import api as v1_api

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

    return app


app = create_app()


def run() -> None:
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
