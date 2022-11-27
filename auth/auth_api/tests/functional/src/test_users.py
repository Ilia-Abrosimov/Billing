import pytest

from src.services.jwt_service import jwt_service
from tests.functional.utils.models import UserOut, Token, AuthHistory, RoleOut


def test_register(session_client):
    """
    Проверка регистрации пользователя
    """
    user_payload = {
        'email': 'test@example.com',
        'password': '12345678'
    }
    response = session_client.post('/auth/api/v1/users/register', json=user_payload)

    assert response.status_code == 201
    assert UserOut(**response.json)


def test_register_not_valid_email(session_client):
    """
    Проверка регистрации с неправильным email
    """
    user_payload = {
        'email': 'user@example',
        'password': 'string'
    }
    response = session_client.post('/auth/api/v1/users/register', json=user_payload)

    assert response.status_code == 400
    assert response.json == {
        'detail': {'json': {'email': ['Not a valid email address.']}},
        'message': 'Validation error'
    }


def test_register_same_email(session_client):
    """
    Проверка регистрации с уже существующим email
    """

    user_payload = {
        'email': 'sametest@example.com',
        'password': '12345678'
    }
    response = session_client.post('/auth/api/v1/users/register', json=user_payload)

    assert response.status_code == 201
    assert UserOut(**response.json)

    response = session_client.post('/auth/api/v1/users/register', json=user_payload)
    assert response.status_code == 400
    assert response.json == {
        'detail': {},
        'message': 'Such email already exists'
    }


@pytest.mark.parametrize(
    'user_agent, login_count',
    [
        ('Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)', 1),
        ('Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko)', 2),

    ]
)
def test_auth_history(session_client, register_user, create_user_with_role, user_agent, login_count):
    """
    Проверка получения истории логинов пользователя
    """
    headers = {
        'User-Agent': user_agent
    }
    response = session_client.post('/auth/api/v1/auth/login', json=register_user, headers=headers)
    assert response.status_code == 200
    token = Token(**response.json)

    headers['Authorization'] = f'Bearer {token.access_token}'
    response = session_client.get('/auth/api/v1/users/auth_history', headers=headers)
    assert response.status_code == 200
    history = AuthHistory(**response.json)
    assert history.pagination.total == login_count


def test_update_user(session_client, update_user, create_user_with_role):
    """
    Проверка изменения данных пользователя
    """
    access_token = jwt_service.add_new_token_pair(create_user_with_role)['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session_client.patch('/auth/api/v1/users/', json=update_user, headers=headers)
    assert response.status_code == 201
    user = UserOut(**response.json)
    assert user.email == update_user['email']


def test_get_user_roles(session_client, create_user_with_role, create_admin_with_role):
    """
    Проверка получения админом ролей пользователя
    """
    access_token = jwt_service.add_new_token_pair(create_admin_with_role)['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session_client.get(f'/auth/api/v1/users/{create_user_with_role.id}/roles', headers=headers)
    assert response.status_code == 200
    assert type(response.json) == list
    assert all([RoleOut(**role) for role in response.json])


def test_add_role_to_user(session_client, create_user_with_role, create_admin_with_role):
    """
    Проверка добавления админом роли пользователю
    """
    access_token = jwt_service.add_new_token_pair(create_admin_with_role)['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    role = {"name": "admin"}
    response = session_client.post(f'/auth/api/v1/users/{create_user_with_role.id}/roles', headers=headers, json=role)
    assert response.status_code == 200
    assert response.json == {"result": True}
