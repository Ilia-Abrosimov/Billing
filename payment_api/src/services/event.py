import json
import logging
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import engine, get_db
from ecom.abstract import EcomEventListener
from ecom.event_listeners import get_event_parser
from models import models
from services.base import BaseService

logger = logging.getLogger(__name__)


class EventService(BaseService):
    def __init__(self, session: AsyncSession, event_parser: EcomEventListener):
        self.event_parser = event_parser
        super().__init__(session)

    async def save_event(self, payload: bytes, headers: dict):
        try:
            event_id = await self.event_parser.validate(payload=payload, headers=headers)
        except BaseException:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)

        query = await self.session.execute(
            select(models.Event).where(models.Event.payment_system_id == event_id)
        )
        db_event = query.scalars().first()
        if db_event:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Duplicate")
        for _ in range(2):
            try:
                db_event = models.Event(
                    payment_system_id=event_id,
                    data=json.loads(payload)
                )
                self.session.add(db_event)
                await self.session.commit()
                break
            except Exception:
                await self.session.rollback()
                logger.exception('Writing event data error')
                Partition = models.Event.create_partition()
                async with engine.begin() as conn:
                    await conn.run_sync(Partition.__table__.create)


@lru_cache()
def get_event_service(
        session: AsyncSession = Depends(get_db),
        event_parser: EcomEventListener = Depends(get_event_parser),
) -> EventService:
    return EventService(session, event_parser)
