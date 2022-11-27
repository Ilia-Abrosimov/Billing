
import logging
from abc import ABC, abstractmethod

from schemas.events import Event, PaymentEvent, PaymentIntent, RefundedCharge

logger = logging.getLogger(__name__)


class EcomEventParser(ABC):
    @abstractmethod
    async def parse(self, event: dict) -> PaymentEvent:
        """Parse webhook event.
            Args:
                payload: Event payload.
                headers: Event headers.

            Returns:
                PaymentEvent: Object that represent parsed webhook event.
        """
        pass


class StripeEventParser(EcomEventParser):
    """Handle Strike Webhook requests."""

    async def _parse_payment_intent(self, payment_intent: dict) -> PaymentIntent:
        intent = PaymentIntent(
            payment_intent=payment_intent['id'],
            customer=payment_intent['customer'],
            status=payment_intent['status'],
        )
        return intent

    async def _payment_intent_succeeded(self, event_object: dict) -> PaymentIntent:
        return await self._parse_payment_intent(event_object)

    async def _payment_intent_canceled(self, event_object: dict) -> PaymentIntent:
        return await self._parse_payment_intent(event_object)

    async def _charge_refunded(self, event_object: dict) -> RefundedCharge:
        refunded_charge = RefundedCharge(
            charge_id=event_object['id'],
            payment_intent=event_object['payment_intent'],
            status=event_object['status'],
        )
        return refunded_charge

    async def parse(self, event: dict) -> PaymentEvent:
        event_type = event['type']
        event_object = event['data']['object']
        logger.info('Handled event type %s', event_type)
        try:
            event_handler = getattr(self, f"_{Event(event_type).name}")
        except (ValueError, AttributeError):
            logger.warning('Unhandled event type %s', event_type)
            return None
        event_data = await event_handler(event_object)
        return PaymentEvent(type=event_type, data=event_data)
