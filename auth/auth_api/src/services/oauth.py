import requests
from apiflask import abort
from flask_security.utils import hash_password

from src.core.oauth import oauth, OAuthProvider
from src.core.utils import get_random_password
from src.db.pg_db import db
from src.models.models import SocialAccount, SocialUser
from src.services import user as user_service, role as role_service


def get_user_social_account(**kwargs):
    return SocialAccount.query.filter_by(**kwargs).first()


def create_social_account_in_db(**kwargs):
    social_account = SocialAccount(**kwargs)
    db.session.add(social_account)
    db.session.commit()
    return social_account


def get_social_redirect_url_or_404(redirect_url, social_name):
    client = get_social_client_or_404(social_name)
    rv = client.create_authorization_url(redirect_url)
    client.save_authorize_data(redirect_uri=redirect_url, **rv)

    url = rv['url']
    return url


def get_social_client_or_404(social_name):
    client = oauth.create_client(social_name)
    if not client:
        abort(404, message="Социальная сеть с таким именем не найдена")
    return client


def get_user_from_social(social_name):
    client = get_social_client_or_404(social_name)
    token = client.authorize_access_token()

    social_user = None

    if social_name == OAuthProvider.yandex.name:
        social_user = get_user_from_yandex(client.api_base_url, token['access_token'])
    elif social_name == OAuthProvider.google.name:
        social_user = get_user_from_google(token)

    social_account = get_user_social_account(social_id=social_user.id, social_name=social_name)
    if social_account:
        return social_account.user

    user = user_service.get_user(email=social_user.email)
    if not user:
        user = user_service.create_user_in_db(email=social_user.email, password=hash_password(get_random_password()))
        users_role = role_service.get_role_by_name('user')
        user_service.add_role_to_user(user, users_role)

    create_social_account_in_db(user_id=user.id, social_id=social_user.id, social_name=social_name)
    return user


def get_user_from_google(token):
    user_info = token.get('userinfo')
    social_user = SocialUser(id=user_info['sub'], email=user_info['email'])
    return social_user


def get_user_from_yandex(url, token):
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'format': 'json',
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    decoded_response = response.json()
    social_user = SocialUser(id=decoded_response['client_id'], email=decoded_response['default_email'])
    return social_user
