import time
from deepface import DeepFace
from typing import Optional
from .base_service import FaceService, EngineType, FaceDetectionResult, \
    FaceMatchResult
from ..core.config import settings


class DeepFaceService(FaceService):
    def __init__(self):
        self._default_threshold = 0.65
        self._detector_backend = "opencv"
        self._distance_metric = "cosine"
        self._model_name = settings.DEEPFACE_MODEL

    @property
    def engine(self) -> EngineType:
        return EngineType.DEEPFACE

    def get_default_threshold(self) -> float:
        return self._default_threshold

    def detect_faces(self, image_path: str) -> FaceDetectionResult:
        start_time = time.time()
        try:
            detections = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend=self._detector_backend,
                enforce_detection=False
            )

            faces = []
            for detection in detections:
                if detection['confidence'] > 0.85:
                    face = detection['facial_area']
                    faces.append({
                        'x': face['x'],
                        'y': face['y'],
                        'width': face['w'],
                        'height': face['h'],
                        'confidence': detection['confidence']
                    })

            return FaceDetectionResult(
                face_count=len(faces),
                faces=faces,
                engine=self.engine,
                processing_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
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

        try:
            # result = DeepFace.verify(
            # data_1, data_2, model_name="VGG-Face",
            # detector_backend="opencv",
            # distance_metric="cosine",
            # enforce_detection=True,
            # align=True,
            # normalization="base")

            result = DeepFace.verify(
                img1_path=image_source_path,
                img2_path=image_cni_path,
                # detector_backend=self._detector_backend,
                # distance_metric=self._distance_metric,
                model_name=self._model_name,
                enforce_detection=True
            )

            print(result)

            similarity = 1 - result['distance']
            matched = similarity >= threshold
            return FaceMatchResult(
                similarity=similarity,
                verified=result['verified'],
                matched=matched,
                engine=self.engine,
                threshold=threshold,
                distance=result['distance'],
                model=self._model_name,
                processing_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return FaceMatchResult(
                similarity=0,
                verified=False,
                engine=self.engine,
                threshold=threshold,
                processing_time_ms=(time.time() - start_time) * 1000,
                matched=False
            )
