from pathlib import Path

import dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = Path(BASE_DIR, '.env')
dotenv.load_dotenv(ENV_FILE)


class PostgresSettings(BaseSettings):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    DATABASE: str

    @property
    def url(self) -> str:
        return f'postgres://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}'

    class Config:
        case_sensitive = False
        env_prefix = "PG_"


class AppSettings(BaseSettings):
    PORT: int = 8080
    IS_DEBUG: bool = False

    TITLE: str = 'LiveCharge API'
    VERSION: str = '0.1.0'

    ADMIN_AUTH_TOKEN: str

    class Config:
        case_sensitive = False


class TestSettings(BaseSettings):
    PG_HOST: str = 'localhost'
    PG_USER: str = 'livechrg-api'
    PG_PASSWORD: str = 'livechrg-api'
    PG_DATABASE: str = 'livechrg-api'
    PG_PORT: int = 5437

    ADMIN_AUTH_TOKEN: str = 'token'

    class Config:
        case_sensitive = False
        env_prefix = "TEST_"