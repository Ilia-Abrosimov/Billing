import logging
import time
from functools import wraps
from http import HTTPStatus
from typing import Optional, List
from uuid import UUID

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger()


class User(BaseModel):
    id: UUID
    roles: List[str]


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        if not credentials:
            return None

        if credentials.scheme != 'Bearer':
            logger.warning(credentials.scheme)
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Invalid authentication scheme.')
        payload = self.verify_jwt(credentials.credentials)
        if not payload:
            logger.warning('PAYLOAD NO')
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Invalid token or expired token.')
        return User(id=payload['sub'], roles=payload['roles'])

    def verify_jwt(self, jwtoken: str) -> Optional[dict]:
        try:
            payload = decode_jwt(jwtoken)
        except jwt.exceptions.PyJWTError:
            payload = None

        return payload


def decode_jwt(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except jwt.exceptions.PyJWTError:
        return {}


def check_role(role_name=None):
    """
    Проверяет есть ли у пользователя роль, которая установлена для защищенного маршрута
    """

    def wrapper(fn):
        @wraps(fn)
        async def decorator(*args, **kwargs):
            if settings.superuser_role_name not in kwargs['user'].roles:
                if not role_name or (role_name not in kwargs['user'].roles):
                    raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
            return await fn(*args, **kwargs)

        return decorator

    return wrapper
