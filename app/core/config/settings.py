from typing import Optional, Union

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator
from pydantic import ValidationInfo


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(
        cls, v: Optional[str], values: ValidationInfo
    ) -> Union[str, MultiHostUrl]:
        if v is not None:
            return v
        required_fields = {
            "POSTGRES_USER": values.data.get("POSTGRES_USER"),
            "POSTGRES_PASSWORD": values.data.get("POSTGRES_PASSWORD"),
            "POSTGRES_HOST": values.data.get("POSTGRES_HOST"),
            "POSTGRES_PORT": values.data.get("POSTGRES_PORT"),
            "POSTGRES_DB": values.data.get("POSTGRES_DB"),
        }

        if any(value is None for value in required_fields.values()):
            missing = [k for k, v in required_fields.items() if v is None]
            raise ValueError(
                f"Missing PostgreSQL connection settings: {', '.join(missing)}"
            )

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=required_fields["POSTGRES_USER"],
            password=required_fields["POSTGRES_PASSWORD"],
            host=required_fields["POSTGRES_HOST"],
            port=required_fields["POSTGRES_PORT"],
            path=required_fields["POSTGRES_DB"] or "",
        )

    model_config = SettingsConfigDict(
        env_file=".env.local",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
