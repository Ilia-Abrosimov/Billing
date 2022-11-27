import pytest
from flask_security.utils import hash_password

from app import create_app
from src.services.role import create_role_in_db
from src.services.user import create_user_in_db, add_role_to_user


@pytest.fixture(scope='session')
def app():
    app = create_app('tests/config.py')
    app.config.update({
        "TESTING": True,
    })

    from src.db.pg_db import init_db, db
    init_db(app)
    app.app_context().push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='session')
def session_client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def register_user():
    return {
        'email': 'user@example.com',
        'password': '12345678'
    }


@pytest.fixture(scope='session')
def update_user():
    return {
        'email': 'user1@example.com',
        'password': '12345678'
    }


@pytest.fixture(scope='session')
def create_user_with_role(register_user):
    user = create_user_in_db(
        email=register_user['email'],
        password=hash_password(register_user['password']))
    role = create_role_in_db(
        {
            'name': 'user',
            'description': 'role for service users'
        }
    )
    add_role_to_user(user, role)
    return user


@pytest.fixture(scope='session')
def create_admin_with_role():
    user = create_user_in_db(
        email='admin@addmin.com',
        password=hash_password('admin@addmin.com'))
    role = create_role_in_db(
        {
            'name': 'admin',
            'description': 'role for admin'
        }
    )
    add_role_to_user(user, role)
    return user
