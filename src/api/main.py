"""FastAPI application entrypoint."""

from fastapi import FastAPI

from src.api.routes import router


app = FastAPI(
    title="MLOps Azure FastAPI Demo",
    description="API base para inferencia y health checks.",
    version="0.1.0",
)

app.include_router(router)
