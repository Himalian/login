from pathlib import Path
from typing import Final

from dotenv import dotenv_values
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv_path = Path(__file__).parent.parent / ".env"  # ../.env


class Settings(BaseSettings):
    USERNAME: Final[str]
    PASSWORD: Final[str]

    model_config = SettingsConfigDict(
        env_file=dotenv_path, env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()  # pyright: ignore

if __name__ == "__main__":
    print(dotenv_path)
    print(settings.model_dump_json())
