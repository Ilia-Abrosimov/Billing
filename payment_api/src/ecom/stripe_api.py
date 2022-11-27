import logging
from typing import List, Tuple

from async_stripe import stripe

from ecom.abstract import EcomClient
from schema.payment import CancelReason, RefundReason
from schema.product import Product

logger = logging.getLogger(__name__)


class StripeClient(EcomClient):
    """Implement Stripe API request and proccess the results."""
    public_key = None

    def __init__(self, secret_key: str, public_key: str, method_types: List[str]) -> None:
        stripe.api_key = secret_key
        self.public_key = public_key
        self.method_types = method_types

    async def create_customer(self, name: str = None, email: str = None, idempotency_key: str = None) -> str:
        """Create customer on ecom side.

            Args:
                name: Name of customer,
                email: Email of customer,
                idempotency_key: Allow to escape duplications.

            Returns:
                str: customer id on ecom side
        """
        customer = await stripe.Customer.create(name=name, email=email, idempotency_key=idempotency_key)
        logger.info('Customer %s created id ', customer.email, customer.id)
        return customer.id

    async def _get_customer_payment_method(self, id: str) -> str:
        methods = await stripe.PaymentMethod.list(customer=id, type=self.method_types[0])
        methods = methods.data
        if methods:
            return methods[0].id
        return None

    async def create_payment_intent(
        self,
        customer_id: str,
        product: Product,
        idempotency_key: str = None,
    ) -> Tuple[str, str]:
        """Create payment intent.

            Args:
                product :  product details.
                idempotency_key: Allow to escape duplications.

            Returns:
                str: Payment id, Client secret.
        """
        intent = await stripe.PaymentIntent.create(
            customer=customer_id,
            amount=product.unit_amount,
            currency=product.currency,
            payment_method_types=['card'],
            setup_future_usage='off_session',
            description=product.product_data.name,
            idempotency_key=idempotency_key,
        )

        logger.info(
            'PaymentIntent id %s created. Customer %s price_data %s',
            intent.id,
            customer_id,
            product.unit_amount,
        )
        return intent.id, intent.client_secret

    async def cancel_payment_intent(
        self,
        payment_intent: str,
        reason: CancelReason = None,
        idempotency_key: str = None
    ) -> None:
        """Cancel payment intent.

            Args:
                payment_intent :  payment_intent id.
                reason: The reason of cancellation.
                idempotency_key: Allow to escape duplications.
        """
        await stripe.PaymentIntent.cancel(
            payment_intent,
            cancellation_reason=reason,
            idempotency_key=idempotency_key,
        )

        logger.info(
            'PaymentIntent id %s cuncelled. Reason %s.',
            payment_intent,
            reason,
        )

    async def charge(self,
                     customer_id: str,
                     product: Product,
                     idempotency_key: str = None
                     ) -> str:
        """Charge client.

            Args:

                customer_id :  Customer to charge.
                product: Product data.
                idempotency_key: Allow to escape duplications.

            Returns:
                str: PaymentIntent id.
        """
        payment_method = await self._get_customer_payment_method(id=customer_id)
        payment = await stripe.PaymentIntent.create(
            amount=product.unit_amount,
            currency=product.currency,
            customer=customer_id,
            payment_method=payment_method,
            off_session=True,
            confirm=True,
            idempotency_key=idempotency_key,
        )
        return payment.id

    async def refund(self,
                     payment_intent: str,
                     amount: int = None,
                     reason: RefundReason = None,
                     idempotency_key: str = None
                     ) -> str:
        """Refund payment.

            Args:

                payment_intent :  Refund payment.
                amount: Refund amount.
                reason: Refund reasin.
                idempotency_key: Allow to escape duplications.

            Returns:
                str: Cahrge id.
        """
        refund = await stripe.Refund.create(
            amount=amount,
            payment_intent=payment_intent,
            reason=reason,
            idempotency_key=idempotency_key,
        )
        logger.info(
            'Refund created: payment %s, amount %s, reason %s, charge %s',
            payment_intent,
            amount,
            reason,
            refund.charge,
        )
        return refund.charge
