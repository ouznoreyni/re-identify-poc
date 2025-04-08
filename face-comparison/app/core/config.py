from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str ="Face Recognition API"
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    TEMP_DIR: str = "./temp"
    KNOWN_FACES_DIR: str = "./static/known_faces"
    API_V1_STR: str = "/api/v1"
    DEEPFACE_MODEL: str = "ArcFace" #Facenet512,
    DEEPFACE_DETECTOR: str = "retinaface"

    class Config:
        env_file = ".env"


settings = Settings()
