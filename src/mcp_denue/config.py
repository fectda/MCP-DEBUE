from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

# Calculate the path to the .env file relative to this file
ENV_PATH = Path(__file__).parent.parent.parent / ".env"


class Config(BaseSettings):
    denue_api_token: str = Field(..., description="API Token for INEGI DENUE")
    denue_base_url: str = Field(
        default="https://www.inegi.org.mx/app/api/denue/v1/consulta/",
        description="Base URL for DENUE API",
    )
    request_timeout: int = Field(default=15, description="Timeout in seconds for API calls")
    max_results_default: int = Field(default=50, description="Default max results for tools")
    rate_limit_throttle: float = Field(
        default=1.0, description="Minimum seconds between requests"
    )

    model_config = SettingsConfigDict(
        env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore"
    )


def get_config() -> Config:
    return Config()  # type: ignore
