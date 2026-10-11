from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "melon"
    db_user: str = "admin_rw"
    db_password: str = ""
    jwt_secret: str
    jwt_expire_minutes: int = 480
    admin_username: str = "admin"
    admin_password: str

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
