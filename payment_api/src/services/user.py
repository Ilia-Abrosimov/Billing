from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import get_db
from models import models
from services.base import BaseService


class UserService(BaseService):

    async def get_user(self, user_id):
        result = await self.session.execute(
            select(models.User).where(models.User.id == user_id)
        )
        return result.scalars().first()

    async def create_user(self, user_id, payment_system_id, is_recurrent_payments):
        user = models.User(
            id=user_id,
            payment_system_id=payment_system_id,
            is_recurrent_payments=is_recurrent_payments
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def change_user_is_recurrent_payments(self, db_user, is_recurrent_payments):
        db_user.is_recurrent_payments = is_recurrent_payments
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user


@lru_cache()
def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)
