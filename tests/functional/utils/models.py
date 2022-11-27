from dataclasses import dataclass

from multidict import CIMultiDictProxy


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@dataclass
class Subscription:
    title: str
    description: str
    price: int
    roles: list[str]


@dataclass
class Payment:
    subscription: str
    start_date: str
