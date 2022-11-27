import logging
from functools import lru_cache
from http import HTTPStatus

from dateutil.relativedelta import relativedelta
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.v1 import schemas
from db.postgres import get_db
from ecom.abstract import EcomClient, get_client
from models import models
from schema.product import Product
from services.base import BaseService
from services.user import UserService, get_user_service

logger = logging.getLogger(__name__)


class PaymentService(BaseService):
    def __init__(self, session: AsyncSession, payment_system_client: EcomClient, user_service: UserService):
        super().__init__(session)
        self.payment_system_client = payment_system_client
        self.user_service = user_service

    async def get_payment(self, user_id, start_date, subscription):
        """Функция ищет оплаченный платеж пользователя по подписке с датой окончания больше,
         чем дата старта, указанная в аргументе"""
        result = await self.session.execute(
            select(models.Payment).join(models.Payment.subscription).where(
                models.Payment.user_id == user_id,
                start_date < models.Payment.end_date,
                models.Subscription.title == subscription,
                models.Payment.is_paid)
        )
        return result.scalars().first()

    async def get_payment_by_intent_id(self, user_id, intent_id):
        """Функция ищет оплаченный платеж пользователя по intent_id"""

        result = await self.session.execute(select(models.Payment).where(
            models.Payment.user_id == user_id,
            models.Payment.intent_id == intent_id,
            models.Payment.is_paid
        ))
        return result.scalars().first()

    async def get_paid_payments(self, user_id, offset=1, limit=1, ):
        """Функция получает все оплаченные платежи пользователя"""
        result = await self.session.execute(
            select(models.Payment)
            .where(
                models.Payment.user_id == user_id,
                models.Payment.is_paid,
            )
            .offset(offset * limit)
            .limit(limit)
            .order_by(models.Payment.id)
        )
        return result.scalars().all()

    async def create_payment(self, user_payment: schemas.UserPayment, subscription):
        db_payment = models.Payment(
            user_id=user_payment.user_id,
            start_date=user_payment.start_date,
            end_date=user_payment.start_date + relativedelta(months=1, days=-1),
            subscription_id=subscription,
            client_secret=user_payment.client_secret,
            intent_id=user_payment.intent_id,
        )
        self.session.add(db_payment)
        await self.session.commit()
        await self.session.refresh(db_payment)
        return db_payment

    async def add_new_payment(self, payment: schemas.Payment, product: Product, user: schemas.User, subscription):
        db_user = await self.user_service.get_user(user.id)
        if not db_user:
            customer_id = await self.payment_system_client.create_customer(
                idempotency_key=str(user.id)
            )
            db_user = await self.user_service.create_user(
                user_id=user.id,
                payment_system_id=customer_id,
                is_recurrent_payments=True
            )

        try:
            intent_id, client_secret = await self.payment_system_client.create_payment_intent(
                customer_id=db_user.payment_system_id,
                product=product,
            )
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Error while getting payment link")

        user_payment = schemas.UserPayment(
            user_id=user.id,
            intent_id=intent_id,
            client_secret=client_secret,
            **payment.dict()
        )
        # TODO записать сумму в базу
        db_payment = await self.create_payment(user_payment, subscription)
        return db_payment

    async def add_new_refund(self, payment_intent, idempotency_key, reason, amount=None):
        try:
            refund = await self.payment_system_client.refund(
                payment_intent=payment_intent,
                amount=amount,
                reason=reason,
                idempotency_key=idempotency_key
            )
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Error while refund")

        return refund


@lru_cache()
def get_payment_service(
        session: AsyncSession = Depends(get_db),
        payment_system_client: EcomClient = Depends(get_client),
        user_service: UserService = Depends(get_user_service),
) -> PaymentService:
    return PaymentService(session, payment_system_client, user_service)
