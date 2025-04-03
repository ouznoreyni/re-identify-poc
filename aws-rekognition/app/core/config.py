from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    max_file_size_mb: int = 5
    PROJECT_NAME: str = "Face Comparison API"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str
    TEMP_DIR: str = "./temp"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()
