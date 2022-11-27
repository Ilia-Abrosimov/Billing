from flask_security.utils import verify_password

from src.models.models import User


def verify_password_by_hash(user: User, password: str) -> str:
    """Проверяет, что пароль, переданный юзером, соответствует хэшу из БД"""
    return verify_password(
        password=password,
        password_hash=user.password
    )
