from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.v1 import schemas
from db.postgres import get_db
from models import models
from services.base import BaseService


class SubscriptionService(BaseService):

    async def create_subscription(self, subscription: schemas.SubscriptionIn):
        db_subscription = models.Subscription(**subscription.dict())
        self.session.add(db_subscription)
        await self.session.commit()
        await self.session.refresh(db_subscription)
        return db_subscription

    async def get_subscription_by_title(self, title):
        result = await self.session.execute(
            select(models.Subscription).where(models.Subscription.title == title)
        )
        return result.scalars().first()

    async def change_subscription(self, subscription: schemas.SubscriptionIn, title: str):
        db_subscription = await self.get_subscription_by_title(title)
        db_subscription.title = title
        db_subscription.description = subscription.description
        db_subscription.price = subscription.price
        db_subscription.roles = subscription.roles
        self.session.add(db_subscription)
        await self.session.commit()
        await self.session.refresh(db_subscription)
        return db_subscription


@lru_cache()
def get_subscription_service(session: AsyncSession = Depends(get_db)) -> SubscriptionService:
    return SubscriptionService(session)
