import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from app.core.config import settings
from app.api.api_v1 import router as api_router
import uvicorn


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for comparing faces using multiple engines:aws_rekognition, face_recognition and deepFace",
    version="1.0.0",
    contact={
        "name": "Ousmane DIOP",
        "email": "ousmanediopp268@gmail.com",
    }
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()


    try:
        response = await call_next(request)
    except Exception as exc:
        raise exc

    process_time = (time.time() - start_time) * 1000
    formatted_time = "{0:.2f}".format(process_time)

    return response


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    #logger.info("Application startup")
    print("Starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    #logger.info("Application shutdown")
    print("Shutting down...")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
