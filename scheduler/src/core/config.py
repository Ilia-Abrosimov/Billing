from pydantic import BaseSettings, Field


class MainSettings(BaseSettings):
    class Config:
        env_file = '../../.env'


class PostgresSettings(MainSettings):
    user: str = Field(..., env='POSTGRES_USER')
    password: str = Field(..., env='POSTGRES_PASSWORD')
    db: str = Field(..., env='POSTGRES_DB')
    host: str = Field(..., env='POSTGRES_HOST')
    # port: int = Field(..., env='POSTGRES_PORT')
    information_period: int = Field(..., env='INFORMATION_PERIOD')


class RedisSettings(MainSettings):
    host: str = Field(..., env='REDIS_HOST')
    port: int = Field(..., env='REDIS_PORT')


class NotificationSettings(BaseSettings):
    host: str = 'rabbit_api'
    port: str = '8000'

    @property
    def dsn(self):
        return f'http://{self.host}:{self.port}/api/v1/event'


db_settings = PostgresSettings()
redis_setting = RedisSettings()
notification_setting = NotificationSettings()
