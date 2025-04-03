from pydantic import BaseModel
from typing import List, Dict, Optional


class FaceMatchDetail(BaseModel):
    confidence: float


class FaceMatch(BaseModel):
    similarity: float
    confidence: float


class ResponseMetadata(BaseModel):
    request_id: str
    http_status_code: int
    retry_attempts: int


class ComparisonResponse(BaseModel):
    source_confidence: float
    source_image: str
    target_image: str
    similarity: float
    face_matches: List[FaceMatch]
    unmatched_faces: int
    metadata: ResponseMetadata

    @classmethod
    def from_aws_response(cls, aws_response: Dict, source_image: str,
                          target_image: str):
        face_matches = [
            FaceMatch(
                similarity=match['Similarity'],
                confidence=match['Face']['Confidence']
            )
            for match in aws_response.get('FaceMatches', [])
        ]

        return cls(
            source_image=source_image,
            target_image=target_image,
            source_confidence=aws_response['SourceImageFace']['Confidence'],
            similarity=face_matches[0].similarity if face_matches else 0.0,
            face_matches=face_matches,
            unmatched_faces=len(aws_response.get('UnmatchedFaces', [])),
            metadata=ResponseMetadata(
                request_id=aws_response['ResponseMetadata']['RequestId'],
                http_status_code=aws_response['ResponseMetadata'][
                    'HTTPStatusCode'],
                retry_attempts=aws_response['ResponseMetadata']['RetryAttempts']
            )
        )


class ErrorResponse(BaseModel):
    detail: str
