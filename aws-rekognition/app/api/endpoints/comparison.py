from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Optional
from app.services import aws_rekognition, validation
from app.schemas.models import ComparisonResponse, ErrorResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/compare-faces/",
    response_model=ComparisonResponse,
    responses={
        413: {"model": ErrorResponse, "description": "File too large"},
        415: {"model": ErrorResponse, "description": "Unsupported media type"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Compare two images using AWS Rekognition",
    description="Compare two images using AWS Rekognition's face comparison feature."
)
async def compare_images(
        image_source: UploadFile = File(...,
                                        description="Source image file (JPG/JPEG/PNG, max 5MB) Ex: captured image"),
        image_target: UploadFile = File(...,
                                        description="Target image file (JPG/JPEG/PNG, max 5MB) Ex: cni image")
):
    """
    Compare two images using AWS Rekognition's face comparison feature.

    - **image_source**: Source image file (max 5MB)
    - **image_target**: Target image file (max 5MB)

    Returns comparison results including similarity score and match information.
    """
    try:
        # Validate both images
        validated_source = validation.validate_image(image_source)
        validated_target = validation.validate_image(image_target)

        # Read image bytes
        source_bytes = await validated_source.read()
        target_bytes = await validated_target.read()

        # Compare faces
        comparison_result = aws_rekognition.rekognition_service.compare_faces(
            source_bytes, target_bytes
        )
        # Format response
        response = ComparisonResponse.from_aws_response(
            aws_response=comparison_result,
            source_image=validated_source.filename,
            target_image=validated_target.filename,
        )
        logger.info("aws response: %s", response, extra=response.dict())
        return response

    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Unexpected error in comparison: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la comparaison des images"
        )
