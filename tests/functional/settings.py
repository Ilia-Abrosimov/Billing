from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    fastapi_host: str = 'http://127.0.0.1'
    fastapi_port: str = '8888'

    subscriptions_router_prefix: str = '/api/v1/subscriptions/'
    payments_router_prefix: str = '/api/v1/payments/'


test_settings = TestSettings()
