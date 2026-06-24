"""Application configuration via environment variables (Spring Boot compatible)."""
from __future__ import annotations
from urllib.parse import urlparse
from pydantic_settings import BaseSettings


def _r2dbc_to_asyncpg(r2dbc_url: str, username: str, password: str) -> str:
    rest = r2dbc_url.removeprefix("r2dbc:")
    parsed = urlparse(rest)
    netloc = f"{username}:{password}@{parsed.hostname}"
    if parsed.port:
        netloc += f":{parsed.port}"
    return f"postgresql+asyncpg://{netloc}{parsed.path}{f'?{parsed.query}' if parsed.query else ''}"


class Settings(BaseSettings):
    # Database (compatible with Spring Boot env vars)
    database_url: str = ""
    spring_r2dbc_url: str = "r2dbc:postgresql://localhost:5432/nexosalud"
    spring_r2dbc_username: str = "postgres"
    spring_r2dbc_password: str = "postgres"

    # Database URL parts (independent of R2DBC, for Coolify/standalone)
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_database: str = "nexosalud"
    pg_user: str = "postgres"
    pg_password: str = "postgres"

    # Server
    server_port: int = 8088
    server_host: str = "0.0.0.0"

    # PDF Service
    pdf_service_url: str = "http://pdf-service:8090"

    # Logging
    log_level: str = "INFO"

    model_config = {"env_prefix": "", "case_sensitive": False}

    @property
    def resolved_database_url(self) -> str:
        """Return the most specific database URL available.

        Priority:
        1. DATABASE_URL (SQLAlchemy native, Coolify preferred)
        2. PG_HOST + PG_USER + PG_PASSWORD + PG_DATABASE (Coolify defaults)
        3. SPRING_R2DBC_* variables (Spring Boot compatibility)
        """
        if self.database_url:
            return self.database_url

        # If the R2DBC URL still has the default value, prefer PG_* parts
        if self.spring_r2dbc_url and "localhost" not in self.spring_r2dbc_url:
            return _r2dbc_to_asyncpg(
                self.spring_r2dbc_url,
                self.spring_r2dbc_username,
                self.spring_r2dbc_password,
            )

        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"


settings = Settings()
