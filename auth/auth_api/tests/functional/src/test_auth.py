from src.services.jwt_service import jwt_service
from tests.functional.utils.models import Token


def test_logout_access_token(session_client, create_user_with_role, register_user):
    """
    Проверяет что токен помещен в черный список и по нему больше нельзя войти
    """
    access_token = jwt_service.add_new_token_pair(create_user_with_role)['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = session_client.delete('/auth/api/v1/auth/logout', headers=headers)
    assert response.status_code == 200
    assert response.json == {'message': 'Access token successfully revoked'}

    response = session_client.get('/auth/api/v1/users/auth_history', headers=headers)
    assert response.status_code == 401
    assert response.json == {'detail': {}, 'message': 'Unauthorized'}


def test_refresh(session_client, create_user_with_role, register_user):
    """
    Проверяет получение новых токенов и их валидность
    """
    refresh_token = jwt_service.add_new_token_pair(create_user_with_role)['refresh_token']
    headers = {'Authorization': f'Bearer {refresh_token}'}
    response = session_client.post('/auth/api/v1/auth/refresh', headers=headers)
    assert response.status_code == 200
    token = Token(**response.json)

    headers = {'Authorization': f'Bearer {token.access_token}'}
    response = session_client.get('/auth/api/v1/users/auth_history', headers=headers)
    assert response.status_code == 200
