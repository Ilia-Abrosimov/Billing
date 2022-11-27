from pydantic import BaseSettings, Field


class DotEnvMixin(BaseSettings):
    class Config:
        env_file = '.env'

class NotificationSettings(DotEnvMixin):
    """Настройки подключения к сервису Уведомлений"""
    host: str = Field(..., env='NOTIFICATION_HOST')
    port: str = Field(..., env='NOTIFICATION_PORT')
    path: str = Field(..., env='NOTIFICATION_API_PATH')

    payment_succeeded_event_name: str = Field(..., env='PAYMENT_SUCCEEDED_EVENT_NAME')
    payment_canceled_event_name: str = Field(..., env='PAYMENT_CANCELED_EVENT_NAME')

    @property
    def notification_url(self):
        return f"http://{self.host}:{self.port}{self.path}"


class AuthSettings(DotEnvMixin):
    """Настройки для связи с нашим сервисом Авторизации"""
    auth_host: str = Field("localhost", env='AUTH_HOST')
    auth_port: int = Field(8999, env='AUTH_PORT')
    superuser_email: str = Field("alexvkleschov@gmail.com", env='AUTH_SUPERUSER_EMAIL')
    superuser_password: str = Field(..., env='AUTH_SUPERUSER_PASSWORD')
    roles_path: str = Field("/auth/api/v1/users/", env='AUTH_ROLES_PATH')
    login_path: str = Field("/auth/api/v1/auth/login", env='AUTH_LOGIN_PATH')
    user_info_path: str = Field("/auth/api/v1/auth/info", env='AUTH_USER_INFO_PATH')

    @property
    def roles_url(self):
        """Получение полного пути к эндпоинту по работе с Ролями"""
        return f"http://{self.auth_host}:{self.auth_port}{self.roles_path}"

    @property
    def login_url(self):
        """Получение полного пути к эндпоинту по авторизации Юзера"""
        return f"http://{self.auth_host}:{self.auth_port}{self.login_path}"


class PostgresSettings(DotEnvMixin):
    user: str = Field("postgres", env='POSTGRES_USER')
    password: str = Field("password", env='POSTGRES_PASSWORD')
    host: str = Field("localhost", env='POSTGRES_HOST')
    port: int = Field(5432, env='POSTGRES_PORT')
    db: str = Field("payments", env='POSTGRES_DB')

    @property
    def dsn(self):
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'


class Settings(DotEnvMixin):
    """Класс, дающий доступ к разным категориям настроек"""
    auth: AuthSettings = AuthSettings()
    postgres: PostgresSettings = PostgresSettings()
    notification: NotificationSettings = NotificationSettings()


# Создаем объект Настроек
settings = Settings()
