"""FastAPI application entrypoint."""

from fastapi import FastAPI

from src.api.routes import router


app = FastAPI(
    title="Azure MLOps Platform - Inference API",
    description="FastAPI service for Iris model health checks, metadata, and inference.",
    version="0.1.0",
)

app.include_router(router)
