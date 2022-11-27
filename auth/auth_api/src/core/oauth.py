import enum

from authlib.integrations.flask_client import OAuth

from src.core.config import oauth_settings
from src.db.redis_db import redis_conn

oauth = OAuth()


class OAuthProvider(enum.Enum):
    yandex = 'yandex'
    google = 'google'


oauth.register(
    name=OAuthProvider.google.name,
    server_metadata_url=oauth_settings.google_server_metadata_url,
    client_kwargs={
        'scope': 'openid email profile'
    }
)
oauth.register(
    name=OAuthProvider.yandex.name,
    access_token_url=oauth_settings.yandex_access_token_url,
    authorize_url=oauth_settings.yandex_authorize_url,
    api_base_url=oauth_settings.yandex_api_base_url,
    client_kwargs={
        'scope': 'login:email login:info'
    }
)


def init_oauth(app):
    oauth.init_app(app, cache=redis_conn)
