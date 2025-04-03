import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class RekognitionService:
    def __init__(self):
        self.client = boto3.client(
            'rekognition',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )

    def compare_faces(self, source_bytes, target_bytes):
        """Compare faces using AWS Rekognition."""
        try:
            response = self.client.compare_faces(
                SourceImage={'Bytes': source_bytes},
                TargetImage={'Bytes': target_bytes},
            )
            return response
        except (BotoCoreError, ClientError) as error:
            logger.error(f"AWS Rekognition error: {str(error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AWS Rekognition error: {str(error)}"
            )
        except Exception as error:
            logger.error(f"Unexpected error: {str(error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(error)}"
            )


rekognition_service = RekognitionService()
