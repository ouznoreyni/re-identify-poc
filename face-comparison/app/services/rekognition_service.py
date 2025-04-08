import boto3
import time
from typing import Optional
from app.core.config import settings
from .base_service import FaceService, EngineType, FaceDetectionResult, \
    FaceMatchResult


class RekognitionService(FaceService):
    def __init__(self):
        self._client = boto3.client(
            'rekognition',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION
        )
        self._default_threshold = 0.7

    @property
    def engine(self) -> EngineType:
        return EngineType.REKOGNITION

    def get_default_threshold(self) -> float:
        return self._default_threshold

    def detect_faces(self, image_path: str) -> FaceDetectionResult:
        start_time = time.time()
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()

            response = self._client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['DEFAULT']
            )

            faces = []
            for face_detail in response['FaceDetails']:
                box = face_detail['BoundingBox']
                faces.append({
                    'left': box['Left'],
                    'top': box['Top'],
                    'width': box['Width'],
                    'height': box['Height'],
                    'confidence': face_detail['Confidence'] / 100
                })

            return FaceDetectionResult(
                face_count=len(faces),
                faces=faces,
                engine=self.engine,
                processing_time_ms=(time.time() - start_time) * 1000
            )
        except Exception:
            return FaceDetectionResult(
                face_count=0,
                faces=[],
                engine=self.engine,
                processing_time_ms=(time.time() - start_time) * 1000
            )

    def compare_faces(
            self,
            image_source_path: str,
            image_cni_path: str,
            threshold: Optional[float] = None
    ) -> FaceMatchResult:
        start_time = time.time()
        threshold = threshold or self._default_threshold
        similarity_threshold = int(threshold * 100)

        try:
            with open(image_source_path, 'rb') as image_source, open(
                    image_cni_path,
                    'rb') as image_cni:
                image_source_bytes = image_source.read()
                image_cni_bytes = image_cni.read()

            response = self._client.compare_faces(
                SourceImage={'Bytes': image_source_bytes},
                TargetImage={'Bytes': image_cni_bytes},
                SimilarityThreshold=similarity_threshold
            )

            if not response['FaceMatches']:
                similarity = 0
                verified = False
            else:
                best_match = response['FaceMatches'][0]
                similarity = best_match['Similarity'] / 100
                verified = similarity >= threshold

            return FaceMatchResult(
                similarity=similarity,
                verified=verified,
                engine=self.engine,
                threshold=threshold,
                model="AWS Rekognition",
                processing_time_ms=(time.time() - start_time) * 1000,
                matched=False
            )
        except Exception:
            return FaceMatchResult(
                similarity=0,
                verified=False,
                engine=self.engine,
                threshold=threshold,
                processing_time_ms=(time.time() - start_time) * 1000,
                matched=False
            )
