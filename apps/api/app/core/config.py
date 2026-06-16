from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_root_env_file() -> str:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / ".env"
        if candidate.exists():
            return str(candidate)
    return ".env"


ROOT_ENV_FILE = _resolve_root_env_file()

class Settings(BaseSettings):
    ENV: str = "dev"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 30

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None
    GOOGLE_LOGIN_SUCCESS_URL: str | None = None
    GOOGLE_ALLOWED_SUCCESS_URLS: str = ""

    APPLE_CLIENT_ID: str | None = None
    APPLE_TEAM_ID: str | None = None
    APPLE_KEY_ID: str | None = None
    APPLE_PRIVATE_KEY: str | None = None
    APPLE_REDIRECT_URI: str | None = None
    APPLE_LOGIN_SUCCESS_URL: str | None = None
    APPLE_ALLOWED_SUCCESS_URLS: str = ""

    EMAIL_FROM: str | None = None
    EMAIL_CODE_TTL_MINUTES: int = 10
    EMAIL_CODE_MIN_SECONDS_BETWEEN_REQUESTS: int = 60
    EMAIL_CODE_MAX_REQUESTS_PER_HOUR: int = 5
    EMAIL_CODE_MAX_ATTEMPTS: int = 5
    AWS_SES_REGION: str = "us-east-1"
    AWS_SES_ACCESS_KEY_ID: str | None = None
    AWS_SES_SECRET_ACCESS_KEY: str | None = None
    AWS_SES_SESSION_TOKEN: str | None = None

    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_BUCKET: str = "nicherides"
    S3_REGION: str = "us-east-1"
    S3_KEY_PREFIX: str = "cars-photos"

    OPENAI_API_KEY: str | None = None
    OPENAI_TEXT_MODEL: str = "gpt-4o-mini"
    PRICE_PREDICTION_API_URL: str = "http://localhost:8001/v1/price/predict"
    PRICE_PREDICTION_API_TIMEOUT_SECONDS: float = 15.0
    VIN_SCAN_DEBUG: bool = False
    VIN_SCAN_API_URL: str = "http://localhost:8001/v1/vin/photo"
    VIN_SCAN_API_TIMEOUT_SECONDS: float = 30.0
    TESSERACT_CMD: str | None = None

    model_config = SettingsConfigDict(
        env_file=(ROOT_ENV_FILE, ".env"),
        extra="ignore",
    )

settings = Settings()
