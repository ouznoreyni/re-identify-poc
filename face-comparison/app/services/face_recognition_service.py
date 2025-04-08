import logging
import face_recognition
import time
from typing import Optional
import numpy as np
from .base_service import FaceService, EngineType, FaceDetectionResult, FaceMatchResult

class FaceRecognitionService(FaceService):
    def __init__(self):
        self._default_threshold = 0.6
        self._tolerance = 0.6
        self.logger = logging.getLogger(__name__)

    @property
    def engine(self) -> EngineType:
        return EngineType.FACE_RECOGNITION

    def get_default_threshold(self) -> float:
        return self._default_threshold

    def detect_faces(self, image_path: str) -> FaceDetectionResult:
        start_time = time.time()
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)

            faces = []
            for (top, right, bottom, left) in face_locations:
                faces.append({
                    'top': top,
                    'right': right,
                    'bottom': bottom,
                    'left': left,
                    'confidence': 1.0
                })

            return FaceDetectionResult(
                face_count=len(faces),
                faces=faces,
                engine=self.engine,
                processing_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            self.logger.error(f"Face detection failed: {str(e)}")
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
        tolerance = 1 - threshold

        try:
            # Load the images
            source_image = face_recognition.load_image_file(image_source_path)
            cni_image = face_recognition.load_image_file(image_cni_path)

            # Get face encodings for each image
            source_encodings = face_recognition.face_encodings(source_image)
            cni_encodings = face_recognition.face_encodings(cni_image)

            # Check if we found any faces in each image
            if not source_encodings or not cni_encodings:
                self.logger.warning("No faces found in one or both images")
                return FaceMatchResult(
                    matched=False,
                    similarity=0,
                    verified=False,
                    engine=self.engine,
                    threshold=threshold,
                    processing_time_ms=(time.time() - start_time) * 1000
                )

            # Compare the first face found in each image
            face_distance = face_recognition.face_distance(
                [cni_encodings[0]],
                source_encodings[0]
            )[0]

            similarity = 1 - face_distance
            verified = face_distance <= tolerance
            matched = verified  # For backward compatibility

            self.logger.info(
                f"Face comparison result - distance: {face_distance:.4f}, "
                f"similarity: {similarity:.4f}, verified: {verified}"
            )

            return FaceMatchResult(
                matched=matched,
                similarity=float(similarity),
                verified=verified,
                engine=self.engine,
                threshold=threshold,
                distance=float(face_distance),
                model="dlib",
                processing_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            self.logger.error(f"Face comparison failed: {str(e)}", exc_info=True)
            return FaceMatchResult(
                matched=False,
                similarity=0,
                verified=False,
                engine=self.engine,
                threshold=threshold,
                distance=1.0,  # Max distance indicates no match
                model="dlib",
                processing_time_ms=(time.time() - start_time) * 1000
            )