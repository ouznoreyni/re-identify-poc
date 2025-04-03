import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1 import router as api_router
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Application lifecycle event handler"""
    logger.info("🚀 Application is starting up...", extra={"app": app})
    print("🚀 Application is starting...")

    yield  # Allow the application to run

    logger.info("🛑 Application is shutting down...")
    print("🛑 Application is shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Face Comparison",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root(request: Request):
    host_url = str(request.base_url).rstrip("/")
    return {
        "message": "Bienvenue sur l'API de comparaison faciale 🎉!",
        "description": "Cette application permet de comparer deux images",
        "documentation": {
            "Swagger UI": f"{host_url}/docs",
            "Redoc": f"{host_url}/redoc"
        }
    }


@app.get("/health", status_code=200, summary="Health Check")
async def health_check():
    """Check if the API is running"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
