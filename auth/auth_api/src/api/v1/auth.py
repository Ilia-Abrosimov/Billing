import logging

from apiflask import APIBlueprint, abort
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, current_user

from src.api.v1.schemas import LoginInfo
from src.services import user as user_service
from src.services.crypto import verify_password_by_hash
from src.services.jwt_service import jwt_service, auth, refresh_auth


auth_route = APIBlueprint(
    name='auth',
    import_name=__name__,
    tag={"name": "Auth", "description": "Базовая аутентификация и работа с JWT"}
)

logger = logging.getLogger()


@auth_route.post('/refresh')
@auth_route.auth_required(refresh_auth)
@jwt_required(refresh=True)
def refresh_tokens():
    """Эндпоинт, которые обрабатывает запрос и при валидном refresh токене возвращает пару токенов access+refresh"""
    # Гасим переданный токен
    token = get_jwt()
    jwt_service.add_token_to_inactive(jti=token['jti'], expiration_time=token['exp'])

    # Возвращаем новые access и refresh
    return jwt_service.add_new_token_pair(current_user)


@auth_route.post('/login')
@auth_route.input(LoginInfo)
def login_user(data):
    """Эндпоинт для того, чтобы Юзер мог авторизоваться"""
    # Проверяем, что данный Юзер есть в базе
    email, password = data['email'], data['password']
    user = user_service.get_user(email=email)
    if not user:
        abort(400, message="Неверные данные для входа")

    # Проверяем совпадение пароля на вход
    is_password_correct = verify_password_by_hash(user=user, password=password)
    if not is_password_correct:
        abort(400, message="Неверные данные для входа")

    # Обновим историю посещений пользователя
    user_service.update_history(user_agent=request.headers.get('User-Agent'), user_id=user.id)

    # Если все проверки пройдены, то отдаем новую пару токенов
    return jwt_service.add_new_token_pair(user)


@auth_route.delete('/logout')
@auth_route.auth_required(auth)
@jwt_required(verify_type=False)
def logout_user():
    """Помещает переданный токен в блоклист"""
    # Проверяем наличие юзера
    if not current_user:
        abort(400, message="Данного Юзера не существует")

    # Добавляем Token в стоп-лист
    token = get_jwt()
    ttype = token['type']
    jwt_service.add_token_to_inactive(jti=token['jti'], expiration_time=token['exp'])

    return jsonify(message=f"{ttype.capitalize()} token successfully revoked")
