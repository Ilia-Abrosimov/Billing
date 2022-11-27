import logging

from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update
from db.postgres import async_db
from models import models

logger = logging.getLogger(__name__)


class DataEnricher:
    """Обрабатывает и обогащает данные об успешных Оплатах"""

    async def get_uncompleted_events(self, model):
        """Получаем те Оплаты, которые отмечены необработанными"""
        async with async_db() as db_session:
            result = await db_session.execute(select(model).where(model.processed == False))
            return result.scalars().all()

    async def get_payment_info(self, payment_id):
        async with async_db() as db_session:
            result = await db_session.execute(select(models.Payment).where(models.Payment.intent_id == payment_id))
            return result.scalars().first()

    async def mark_event_as_completed(self, model, id, **kwargs):
        """Отмечает Оплату как успешную"""
        async with async_db() as db_session:
            query = (
                sqlalchemy_update(model).where(model.payment_system_id == id).values(
                    **kwargs).execution_options(synchronize_session="fetch")
            )
            await db_session.execute(query)
            await db_session.commit()

    async def mark_payment_as_completed(self, model, id, **kwargs):
        """Отмечает Оплату как успешную"""
        async with async_db() as db_session:
            query = (
                sqlalchemy_update(model).where(model.intent_id == id).values(
                    **kwargs).execution_options(synchronize_session="fetch")
            )
            await db_session.execute(query)
            await db_session.commit()
