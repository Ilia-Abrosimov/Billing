from src.services.jwt_service import jwt_service
from tests.functional.utils.models import RoleOut


def test_get_roles_by_admin(session_client, create_admin_with_role):
    """
    Проверка получения админом ролей пользователя
    """
    access_token = jwt_service.add_new_token_pair(create_admin_with_role)['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session_client.get('/auth/api/v1/roles/', headers=headers)
    assert response.status_code == 200
    assert type(response.json) == list
    assert all([RoleOut(**role) for role in response.json])


def test_error_get_roles_by_user(session_client, create_user_with_role):
    """
    Проверка запрета доступа без роли admin
    """
    access_token = jwt_service.add_new_token_pair(create_user_with_role)['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session_client.get('/auth/api/v1/roles/', headers=headers)
    assert response.status_code == 403
    assert response.json == {'detail': {}, 'message': 'Forbidden'}


def test_add_role_by_admin(session_client, create_admin_with_role):
    """
    Проверка создания и получения роли
    """
    role = {
        'description': 'some new role',
        'name': 'new_role'
    }
    access_token = jwt_service.add_new_token_pair(create_admin_with_role)['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session_client.post('/auth/api/v1/roles/', headers=headers, json=role)
    assert response.status_code == 201
    role_out = RoleOut(**response.json)

    headers = {'Authorization': f'Bearer {access_token}'}
    response = session_client.get(f'/auth/api/v1/roles/{role_out.id}', headers=headers)
    assert response.status_code == 200
    assert RoleOut(**response.json)
