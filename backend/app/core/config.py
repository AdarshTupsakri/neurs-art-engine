"""Application settings, loaded from environment variables (or a local .env file)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "NEURS Art Engine API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # --- Gemini ---
    GEMINI_API_KEY: str = ""
    GEMINI_IMAGE_MODEL: str = "gemini-3.1-flash-image"
    # When true, requests without a working Gemini key fall back to the offline demo /
    # computer-vision generators instead of returning 503. Handy for local dev & CI.
    ALLOW_OFFLINE_FALLBACK: bool = True

    # --- Sheet layout (one Gemini call -> one sheet -> N registered panels) ---
    SHEET_ROWS: int = 2
    SHEET_COLS: int = 3
    STAGE_COUNT: int = 5

    # --- Uploads ---
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024
    MAX_IMAGE_SIDE: int = 1024  # uploads are downscaled to this before processing

    # --- CORS ---
    # Comma-separated explicit origins, plus a regex so any Cloudflare Pages preview works.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    CORS_ORIGIN_REGEX: str = r"https://([a-z0-9-]+\.)*pages\.dev"

    LOG_LEVEL: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
