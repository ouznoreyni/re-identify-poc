from fastapi import HTTPException, status
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/jpg']


def validate_image(file):
    """Validate the uploaded image file."""
    # Check file size
    file.file.seek(0, 2)  # Move to end of file
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer

    max_size = settings.max_file_size_mb * 1024 * 1024

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop volumineux. La taille maximale autorisée est de {settings.max_file_size_mb}MB."
        )

    # Check content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Seuls les formats JPG, JPEG et PNG sont autorisés."
        )

    return file
