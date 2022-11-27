import logging
from functools import lru_cache

import stripe

from ecom.abstract import EcomEventListener

logger = logging.getLogger(__name__)

event_listener = None


class StripeEventListener(EcomEventListener):
    """Handle Strike Webhook requests."""

    def __init__(self, endpoint_secret: str) -> None:
        self.endpoint_secret = endpoint_secret

    async def validate(self, payload: bytes, headers: dict) -> str:
        try:
            stripe_signature = headers['stripe-signature']
        except KeyError as e:
            logger.warning('Header stripe_signature does not exists %s', headers)
            raise e
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, self.endpoint_secret
            )
        except ValueError as e:
            logger.warning('Invalid payload %s', payload)
            raise e
        except stripe.error.SignatureVerificationError as e:
            logger.warning('Invalid signature %s', payload)
            raise e
        return event.id


@lru_cache()
def get_event_parser() -> EcomEventListener:
    return event_listener
