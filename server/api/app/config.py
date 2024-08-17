from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    PydanticBaseSettingsSource,
)
from typing import Tuple, Type
from pydantic import BaseModel

# Read More on Pydantic Settings and TOML here https://docs.pydantic.dev/latest/concepts/pydantic_settings/#other-settings-source


class Mqtt(BaseModel):
    broker: str
    port: int
    client: str
    topic: str


class Database(BaseModel):
    db_hostname: str
    db_port: int
    db_name: str
    user: str
    password: str


class Settings(BaseSettings):
    mqtt: Mqtt
    database: Database
    model_config = SettingsConfigDict(toml_file="config.toml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)
