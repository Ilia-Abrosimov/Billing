from pydantic import Field

from src.core.config import api_settings, MainSettings


class PostgresSettings(MainSettings):
    postgres_user: str = Field(..., env='TEST_POSTGRES_USER')
    postgres_password: str = Field(..., env='TEST_POSTGRES_PASSWORD')
    postgres_db: str = Field(..., env='TEST_POSTGRES_DB')
    postgres_host: str = Field(..., env='TEST_POSTGRES_HOST')
    postgres_port: int = Field(..., env='TEST_POSTGRES_PORT')


pg_settings = PostgresSettings()

SECRET_KEY = api_settings.secret_key
SECURITY_PASSWORD_SALT = api_settings.salt
JWT_TOKEN_LOCATION = ["headers"]
JWT_ACCESS_TOKEN_EXPIRES = api_settings.access_jwt_token_duration
JWT_REFRESH_TOKEN_EXPIRES = api_settings.refresh_jwt_token_duration
SUPERUSER_ROLE_NAME = api_settings.superuser_role_name
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{db}'.format(
    user=pg_settings.postgres_user,
    password=pg_settings.postgres_password,
    host=pg_settings.postgres_host,
    port=pg_settings.postgres_port,
    db=pg_settings.postgres_db,
)
