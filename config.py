from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    mongodb_uri: str = Field(
        validation_alias=AliasChoices("mongodb_uri", "MONGODB_URI")
    )
    database_name: str = Field(
        "worldchat",
        validation_alias=AliasChoices("database_name", "DATABASE_NAME"),
    )
    jwt_secret: str = Field(
        validation_alias=AliasChoices("jwt_secret", "JWT_SECRET")
    )
    jwt_algorithm: str = Field(
        "HS256",
        validation_alias=AliasChoices("jwt_algorithm", "JWT_ALGORITHM"),
    )
    access_token_expire_minutes: int = Field(
        10080,
        validation_alias=AliasChoices(
            "access_token_expire_minutes", "ACCESS_TOKEN_EXPIRE_MINUTES"
        ),
    )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
