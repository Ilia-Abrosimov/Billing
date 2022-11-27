import datetime as dt
import logging
from functools import wraps

from apiflask import abort, HTTPTokenAuth
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request, get_jwt

from src.core.utils import get_unix_timedelta
from src.db.pg_db import db
from src.db.redis_db import redis_service
from src.models.models import Token, User
from src.services import user as user_service

from src.services.user import get_actual_user_roles

logger = logging.getLogger()
auth = HTTPTokenAuth(description='Enter JWT Bearer token')
refresh_auth = HTTPTokenAuth(description='Enter refresh JWT Bearer token')


class JWTService:
    """Управляет валидацией и выдачей токенов"""

    def __init__(self, permanent_storage, no_sql_storage=None):
        self.permanent_storage = permanent_storage
        self.no_sql_storage = no_sql_storage

    def add_new_token_pair(self, user: User) -> dict | None:
        """Создает пару новых токенов - access и refresh"""
        new_access_token = self._create_new_access_token(user)
        new_refresh_token = self._create_new_refresh_token(user.id)

        return {
            "message": "Success",
            'access_token': new_access_token.token,
            "refresh_token": new_refresh_token.token
        }

    def _create_new_access_token(self, user: User) -> Token:
        roles = [role.name for role in get_actual_user_roles(user)]
        new_access_token = create_access_token(identity=user.id, additional_claims={'roles': roles})
        return Token(
            token=new_access_token,
            token_type="access"
        )

    def _create_new_refresh_token(self, identity: str) -> Token:
        new_refresh_token = create_refresh_token(identity=identity)
        return Token(
            token=new_refresh_token,
            token_type="refresh"
        )

    def add_token_to_inactive(self, jti: str, expiration_time: str):
        """Добавит данный JTI в стоп-лист на оставшееся время жизни токена"""
        seconds_to_expire = get_unix_timedelta(expiration_time)

        self.no_sql_storage.set(
            name=jti,
            value="",
            time=dt.timedelta(seconds=seconds_to_expire),
        )


def check_role_jwt(role_name):
    """
    Проверяет есть ли у пользователя роль, которая установлена для защищенного маршрута или ороль суперпользователя
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if (role_name in claims['roles']) or (current_app.config['SUPERUSER_ROLE_NAME'] in claims['roles']):
                return fn(*args, **kwargs)
            else:
                abort(403, message='Forbidden')

        return decorator

    return wrapper


@auth.verify_token
def verify_token(token):
    try:
        _, jwt_data = verify_jwt_in_request()
    except:  # noqa: E722
        return False
    if 'sub' in jwt_data:
        return user_service.get_user(id=jwt_data['sub'])


@refresh_auth.verify_token
def verify_token(token):
    try:
        _, jwt_data = verify_jwt_in_request(refresh=True)
    except:  # noqa: E722
        return False
    if 'sub' in jwt_data:
        return user_service.get_user(id=jwt_data['sub'])


jwt_service = JWTService(
    permanent_storage=db,
    no_sql_storage=redis_service
)
