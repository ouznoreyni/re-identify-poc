from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, List, Optional
from enum import Enum

class EngineType(str, Enum):
    DEEPFACE = "deep_face"
    FACE_RECOGNITION = "face_recognition"
    REKOGNITION = "aws_rekognition"

class FaceDetectionResult(BaseModel):
    face_count: int
    faces: List[Dict[str, float]]
    engine: EngineType
    processing_time_ms: float

class FaceMatchResult(BaseModel):
    similarity: float
    verified: bool
    matched: bool
    engine: EngineType
    threshold: float
    distance: Optional[float] = None
    model: Optional[str] = None
    processing_time_ms: float

class FaceService(ABC):
    @property
    @abstractmethod
    def engine(self) -> EngineType:
        pass

    @abstractmethod
    def detect_faces(self, image_path: str) -> FaceDetectionResult:
        pass

    @abstractmethod
    def compare_faces(
            self,
            image_source_path: str,
            image_cni_path: str,
            threshold: Optional[float] = None
    ) -> FaceMatchResult:
        pass

    @abstractmethod
    def get_default_threshold(self) -> float:
        pass