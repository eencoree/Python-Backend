from functools import lru_cache

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

class ApiPrefix(BaseModel):
    prefix: str = '/api'

class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

class RedisConfig(BaseModel):
    url: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env.example', '.env',),
        env_prefix='CONFIG__',
        env_nested_delimiter='__',
        case_sensitive=False,
        extra='ignore'
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig
    redis: RedisConfig
    api: ApiPrefix = ApiPrefix()

@lru_cache
def get_settings() -> Settings:
    return Settings()