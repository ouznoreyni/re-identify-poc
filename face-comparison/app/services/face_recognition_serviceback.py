import logging

import face_recognition
import time
from typing import Optional

import numpy as np

from .base_service import FaceService, EngineType, FaceDetectionResult, \
    FaceMatchResult


class FaceRecognitionService(FaceService):
    def __init__(self):
        self._default_threshold = 0.6
        self._tolerance = 0.6

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
        tolerance = 1 - threshold
        print("-------")
        try:
            image_source = face_recognition.load_image_file(image_source_path)
            image_cni = face_recognition.load_image_file(image_cni_path)

            encodings_image_source = face_recognition.face_encodings(
                image_source)
            encodings_image_cni = face_recognition.face_encodings(image_cni)

            if not encodings_image_cni or not encodings_image_source:
                return FaceMatchResult(
                    matched=False,
                    similarity=0,
                    verified=False,
                    engine=self.engine,
                    threshold=threshold,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            print("-------")
            distance = face_recognition.face_distance([encodings_image_cni],
                                                      encodings_image_source)
            print("distance")
            match_results = face_recognition.compare_faces(
                [encodings_image_cni], encodings_image_source)
            best_match_index = np.argmin(distance)
            print("best_match_index", best_match_index)
            print("distance[best_match_index]", distance[best_match_index])
            print("len(encodings_image_cni)", len(encodings_image_cni))
            print("len(encodings_image_source)", len(encodings_image_source))
            print("distance", distance)
            print("best_match_index", best_match_index)
            logging.info("------------------")
            similarity = 1 - distance
            verified = distance <= tolerance
            return FaceMatchResult(
                similarity=float(similarity),
                verified=verified,
                engine=self.engine,
                threshold=threshold,
                distance=float(distance),
                model="dlib",
                processing_time_ms=(time.time() - start_time) * 1000,
                matched=False
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
