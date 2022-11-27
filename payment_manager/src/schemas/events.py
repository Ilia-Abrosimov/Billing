from enum import Enum
from typing import Union

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default) -> str:
    """Fast json dumps."""
    return orjson.dumps(v, default=default).decode()


class OrjsonModel(BaseModel):
    """Fast json serializer."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PaymentIntent(OrjsonModel):
    payment_intent: str
    customer: str
    status: str

    class Config:
        orm_mode = True


class RefundedCharge(OrjsonModel):
    charge_id: str
    payment_intent: str
    status: str


class Event(Enum):
    charge_refunded = 'charge.refunded'
    payment_intent_canceled = 'payment_intent.canceled'
    payment_intent_succeeded = 'payment_intent.succeeded'


class PaymentEvent(OrjsonModel):
    type: Event
    data: Union[PaymentIntent, RefundedCharge]

    class Config:
        orm_mode = True
