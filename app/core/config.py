from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase anon key")

    # Optional settings with defaults
    DEBUG: bool = Field(False, description="Enable debug mode")
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
