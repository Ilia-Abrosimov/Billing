import click
import sentry_sdk
from apiflask import APIFlask
from flask import request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sentry_sdk.integrations.flask import FlaskIntegration
from src.api.v1.auth import auth_route
from src.api.v1.oauth import oauth_route
from src.api.v1.roles import roles_route
from src.api.v1.users import users_route
from src.core.config import api_settings, sentry_settings
from src.core.limiters import limiter
from src.core.logger import logging
from src.core.oauth import init_oauth
from src.db.pg_db import db, init_db
from src.db.redis_db import redis_service
from src.models.models import Role, User
from src.services.role import create_role_in_db, get_role_by_name
from src.services.user import add_role_to_user, create_user_in_db, get_user

sentry_sdk.init(
    dsn=sentry_settings.dsn,
    integrations=[
        FlaskIntegration(),
    ],
    traces_sample_rate=sentry_settings.traces_sample_rate,
)


def create_app(config_path):
    app = APIFlask(__name__, docs_path='/', title='Authorization Service API', version='1.0')
    app.config.from_pyfile(config_path)
    app.logger = logging.getLogger(__name__)

    init_db(app)
    SQLAlchemyInstrumentor().instrument(engine=db.engine)
    jwt = JWTManager(app)

    Migrate(app, db)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        """Колбэк, который проверяет, находится ли токен среди отозванных токенов в Рэдис. Если функция возвращает True,
        то эндпоинты, защищенные jwt_required(), возвратят сообщение 'Token has been revoked'
        """
        jti = jwt_payload["jti"]
        token_in_redis = redis_service.get(jti)

        return token_in_redis is not None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Callback для поиска пользователя
        """
        identity = jwt_data["sub"]
        user = get_user(id=identity)
        return user

    limiter.init_app(app)

    init_oauth(app)

    # Регистрируем эндпоинты
    api_v1 = '/auth/api/v1'
    app.register_blueprint(roles_route, url_prefix=f'{api_v1}/roles')
    app.register_blueprint(auth_route, url_prefix=f'{api_v1}/auth')
    app.register_blueprint(users_route, url_prefix=f'{api_v1}/users')
    app.register_blueprint(oauth_route, url_prefix=f'{api_v1}/oauth')
    return app


# Создаем приложение и подключаем конфиги
app = create_app('src/core/config.py')


# @app.before_request
# def before_request():
#     request_id = request.headers.get('X-Request-Id')
#     if not request_id:
#         raise RuntimeError('request id is required')


# Конфигурируем и добавляем трейсер
# configure_tracer()
# FlaskInstrumentor().instrument_app(app)


@app.cli.command("create-superuser")
@click.argument("email")
@click.argument("password")
def create_superuser(email: str, password: str) -> None:
    """Консольная команда для добавления суперюзера"""
    # Проверим существование Роли и добавим при необходимости
    if not get_role_by_name(api_settings.superuser_role_name):
        create_role_in_db(
            {
                'name': api_settings.superuser_role_name,
                'description': "This Role exists only for admins"
            }
        )
    if not get_role_by_name(api_settings.guest_role_name):
        create_role_in_db(
            {
                'name': api_settings.guest_role_name,
                'description': "Guest user role"
            }
        )

    # Добавим Юзера
    if not get_user(email=email):
        create_user_in_db(email=email, password=hash_password(password))

    # Добавим Юзеру Админскую Роль
    created_user = get_user(email=email)
    superuser_role = get_role_by_name(api_settings.superuser_role_name)
    add_role_to_user(created_user, superuser_role)

    return None


if __name__ == '__main__':
    app.run(debug=api_settings.flask_debug)
