import asyncio

import aiohttp
import pytest
import pytest_asyncio

from settings import test_settings

from utils.models import HTTPResponse

FASTAPI_URL = f'{test_settings.fastapi_host}:{test_settings.fastapi_port}'


@pytest.fixture(scope='session')
def event_loop():
    yield asyncio.get_event_loop()


@pytest_asyncio.fixture(scope='session')
async def session():
    """Возвращает интерфейс для проведения HTTP запросов"""
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
def make_get_request(session):
    """Фикстура для отправки GET запросов.
    """

    async def inner(endpoint: str, params: dict | None = None) -> HTTPResponse:
        params = params or {}
        url = f'{FASTAPI_URL}{endpoint}'
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest_asyncio.fixture
def make_post_request(session):
    """Фикстура для отправки POST запросов.
    """

    async def inner(endpoint: str, params: dict | None = None, headers: dict | None = None,
                    body: dict | None = None) -> HTTPResponse:
        params = params or {}
        url = f'{FASTAPI_URL}{endpoint}'
        async with session.post(url, params=params, headers=headers, json=body) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest_asyncio.fixture
def make_patch_request(session):
    """Фикстура для отправки PUT запросов.
    """

    async def inner(endpoint: str, params: dict | None = None, headers: dict | None = None,
                    body: dict | None = None) -> HTTPResponse:
        params = params or {}
        url = f'{FASTAPI_URL}{endpoint}'
        async with session.patch(url, params=params, headers=headers, json=body) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
