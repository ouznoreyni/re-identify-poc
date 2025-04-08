from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.params import Form
from fastapi.responses import JSONResponse
from app.services.factory import FaceServiceFactory
from app.services.base_service import EngineType
import os
import uuid
from typing import Annotated
from app.core.config import settings

router = APIRouter()


def save_upload_file(upload_file: UploadFile, directory: str) -> str:
    try:
        os.makedirs(directory, exist_ok=True)
        file_ext = os.path.splitext(upload_file.filename)[1]
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        temp_filepath = os.path.join(directory, temp_filename)

        with open(temp_filepath, "wb") as buffer:
            buffer.write(upload_file.file.read())


        return temp_filepath
    except Exception as e:

        raise HTTPException(status_code=500, detail="File upload failed")


@router.post("/compare/{engine}")
async def compare_faces(
        engine: EngineType,
        image_source: UploadFile = File(...),
        image_cni: UploadFile = File(...),
        threshold: float = None,
):

    try:
        engine_type = EngineType(engine.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engine specified")

    service = FaceServiceFactory.create_service(engine_type)

    image_source_path = save_upload_file(image_source, settings.TEMP_DIR)
    image_cni_path = save_upload_file(image_cni, settings.TEMP_DIR)

    try:
        result = service.compare_faces(image_source_path, image_cni_path,
                                       threshold)
        return JSONResponse(content=result.model_dump())
    finally:
        os.remove(image_source_path)
        os.remove(image_cni_path)


@router.post("/compare/all")
async def compare_all_engines(
        image_source: UploadFile = File(...),
        image_cni: UploadFile = File(...)
):

    image_source_path = save_upload_file(image_source, settings.TEMP_DIR)
    image_cni_path = save_upload_file(image_cni, settings.TEMP_DIR)

    results = {}

    try:
        for engine in EngineType:
            service = FaceServiceFactory.create_service(engine)
            result = service.compare_faces(image_source_path, image_cni_path)
            results[engine.value] = result.model_dump()

        similarities = [v['similarity'] for v in results.values()]
        avg_similarity = sum(similarities) / len(similarities)

        verifications = [v['verified'] for v in results.values()]
        consensus = sum(verifications) >= 2  # At least 2 out of 3 agree

        response = {
            "results": results,
            "summary": {
                "average_similarity": avg_similarity,
                "consensus_verification": consensus,
                "engines_agree": sum(verifications) if consensus else len(
                    verifications) - sum(verifications)
            }
        }

        return JSONResponse(content=response)
    finally:
        os.remove(image_source_path)
        os.remove(image_cni_path)
