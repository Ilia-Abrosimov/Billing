from typing import List
from uuid import UUID
from http import HTTPStatus
import logging

import aiohttp


logger = logging.getLogger(__name__)


class RoleUpdater:
    """Добавляет роли Пользователя, используя удаленный сервис Авторизации"""

    def __init__(self, roles_url: str, login_url: str, superuser_email: str, superuser_pass: str):
        self.roles_url = roles_url
        self.login_url = login_url
        self.superuser_email = superuser_email
        self.superuser_pass = superuser_pass
        self.superuser_access_token = None

    @staticmethod
    async def _send_async_request(method: str, url: str, **kwargs):
        """Отправляет асинхронный запрос на указанный URL"""
        conn = aiohttp.TCPConnector(limit_per_host=5)
        async with aiohttp.ClientSession(connector=conn, trust_env=True) as session:
            try:
                request_method = getattr(session, method)
            except (ValueError, AttributeError):
                logger.warning('Unhandled request type %s', method)
                return
            return await request_method(url, **kwargs)

    async def _get_superuser_access_token(self) -> None:
        """Позволяет обновить access token Суперюзера"""
        payload = {"email": self.superuser_email, "password": self.superuser_pass}
        response = await self._send_async_request('post', self.login_url, json=payload)
        # Обрабатываем ответ
        if response.status == HTTPStatus.OK:
            # Получаем access token
            data = await response.json()
            access_token = data["access_token"]
            logging.warning("Admin did login")

            self.superuser_access_token = access_token

            return None

    async def add_roles(self, users: List[UUID], roles: List[str], expired_at: str) -> None:
        """Позволяет разом добавить Роли списку Пользователей"""
        # Для каждого Пользователя и для каждой Роли:
        for user in users:
            for role in roles:
                url = f"{self.roles_url}/{user}/roles"
                # Если мы не запрашивали access token, то следует запросить
                if not self.superuser_access_token:
                    await self._get_superuser_access_token()
                # Формируем данные для запроса
                headers = {"Authorization": f"Bearer {self.superuser_access_token}"}
                payload = {"name": role, "date": expired_at}
                # Отправляем запрос
                response = await self._send_async_request('post', url, json=payload, headers=headers)
                logger.warning(f"HTTP Response: {response}")
                # Если Access Token потерял актуальность, то обновляем его и переотправляем запрос
                if response.status == HTTPStatus.FORBIDDEN:
                    await self._get_superuser_access_token()
                    await self._send_async_request('post', url, json=payload, headers=headers)

    async def delete_roles(self, users: List[UUID], roles: List[str], expired_at: str) -> None:
        """Позволяет разом удалить Роли списку Пользователей"""
        for user in users:
            for role in roles:
                url = f"{self.roles_url}/{user}/roles"
                if not self.superuser_access_token:
                    await self._get_superuser_access_token()
                headers = {"Authorization": f"Bearer {self.superuser_access_token}"}
                payload = {"name": role, "date": expired_at}
                response = await self._send_async_request('delete', url, json=payload, headers=headers)
                logger.warning(f"HTTP Response: {response}")
                if response.status == HTTPStatus.FORBIDDEN:
                    await self._get_superuser_access_token()
                    await self._send_async_request('delete', url, json=payload, headers=headers)
