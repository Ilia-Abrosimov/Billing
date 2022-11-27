from pydantic import BaseSettings, Field


# Environment Settings
class MainSettings(BaseSettings):
    class Config:
        env_file_encoding = 'utf-8'
        use_enum_values = True
        env_file = '.env'


class ApiSettings(MainSettings):
    secret_key: str = Field(..., env='SECRET_KEY')
    salt: str = Field(..., env='SALT')
    flask_debug: bool = Field(False, env='FLASK_DEBUG')
    refresh_jwt_token_duration: int = Field(False, env='REFRESH_JWT_TOKEN_DURATION')
    access_jwt_token_duration: int = Field(False, env='ACCESS_JWT_TOKEN_DURATION')
    superuser_role_name: str = Field(False, env='SUPERUSER_ROLE_NAME')
    guest_role_name: str = Field(False, env='GUEST_ROLE_NAME')
    # Limiter settings
    limiter_config: str = Field(..., env='LIMITER_CONFIG')


class RedisSettings(MainSettings):
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(..., env='REDIS_PORT')


class PostgresSettings(MainSettings):
    postgres_user: str = Field(..., env='POSTGRES_USER')
    postgres_password: str = Field(..., env='POSTGRES_PASSWORD')
    postgres_db: str = Field(..., env='POSTGRES_DB')
    postgres_host: str = Field(..., env='POSTGRES_HOST')
    postgres_port: int = Field(..., env='POSTGRES_PORT')


class JaegerSettings(MainSettings):
    agent_host: str = Field(..., env='JAEGER_HOST')
    agent_port: int = Field(..., env='JAEGER_AGENT_PORT')
    sampling_ratio: float = Field(..., env='JAEGER_SAMPLING_RATIO')
    auth_project_name: str = Field(..., env='AUTH_PROJECT_NAME')


class OauthClientSettings(MainSettings):
    google_client_id: str = Field(..., env='GOOGLE_CLIENT_ID')
    google_client_secret: str = Field(..., env='GOOGLE_CLIENT_SECRET')
    google_server_metadata_url: str = Field(
        'https://accounts.google.com/.well-known/openid-configuration',
        env='GOOGLE_SERVER_METADATA_URL'
    )

    yandex_client_id: str = Field(..., env='YANDEX_CLIENT_ID')
    yandex_client_secret: str = Field(..., env='YANDEX_CLIENT_SECRET')
    yandex_access_token_url: str = Field('https://oauth.yandex.ru/token', env='YANDEX_ACCESS_TOKEN_URL')
    yandex_authorize_url: str = Field('https://oauth.yandex.ru/authorize', env='YANDEX_AUTHORIZE_URL')
    yandex_api_base_url: str = Field('https://login.yandex.ru/info', env='YANDEX_API_BASE_URL')


class SentrySettings(MainSettings):
    dsn: str
    traces_sample_rate: float = 1.0

    class Config:
        env_prefix = 'sentry_'


redis_settings = RedisSettings()
pg_settings = PostgresSettings()
api_settings = ApiSettings()
jaeger_settings = JaegerSettings()
oauth_settings = OauthClientSettings()
sentry_settings = SentrySettings()

# Flask Configuration
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

GOOGLE_CLIENT_ID = oauth_settings.google_client_id
GOOGLE_CLIENT_SECRET = oauth_settings.google_client_secret

YANDEX_CLIENT_ID = oauth_settings.yandex_client_id
YANDEX_CLIENT_SECRET = oauth_settings.yandex_client_secret
