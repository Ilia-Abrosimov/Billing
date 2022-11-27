import datetime as dt
import secrets
import string

from user_agents import parse
from enum import Enum


class UserDeviceType(Enum):
    WEB = 'Браузер'
    MOBILE = 'Телефон'
    SMART = 'Смарт-ТВ'


def useragent_device_parser(useragent: str) -> UserDeviceType | None:
    """Считывает устройство из строки Юзер-Агента"""
    user_agent = parse(useragent)
    # Парсим устройства
    if str(user_agent).find("TV") != -1:
        return UserDeviceType.SMART
    if user_agent.is_mobile or user_agent.is_tablet:
        return UserDeviceType.MOBILE
    if user_agent.is_pc:
        return UserDeviceType.WEB

    return UserDeviceType.WEB


def get_unix_timedelta(unix_time: str | dt.datetime | int):
    """Определяет дельту между текущим UNIX-временем и переданным в качестве параметра"""
    end_timestamp = unix_time
    if isinstance(unix_time, (int, str)):
        end_timestamp = dt.datetime.fromtimestamp(float(unix_time)).timestamp()

    return end_timestamp - dt.datetime.now().timestamp()


def get_random_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password
