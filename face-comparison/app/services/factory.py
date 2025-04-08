from .deepface_service import DeepFaceService
from .face_recognition_service import FaceRecognitionService
from .rekognition_service import RekognitionService
from .base_service import EngineType, FaceService


class FaceServiceFactory:
    @staticmethod
    def create_service(engine: EngineType) -> FaceService:
        if engine == EngineType.DEEPFACE:
            return DeepFaceService()
        elif engine == EngineType.FACE_RECOGNITION:
            return FaceRecognitionService()
        elif engine == EngineType.REKOGNITION:
            return RekognitionService()
        raise ValueError(f"Unknown engine type: {engine}")
