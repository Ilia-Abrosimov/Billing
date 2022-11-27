import logging

from fastapi import APIRouter, Depends, Request

from api.v1 import schemas
from services.event import EventService, get_event_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/', response_model=schemas.WebhookResponse, summary='Webhook')
async def save_event(request: Request,
                     event_service: EventService = Depends(get_event_service),
                     ):
    payload = await request.body()
    await event_service.save_event(payload=payload, headers=request.headers)
    return schemas.WebhookResponse(success=True)
