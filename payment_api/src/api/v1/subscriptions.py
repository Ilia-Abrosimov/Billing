import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from api.v1 import schemas
from services.auth import JWTBearer, check_role
from services.subscruption import SubscriptionService, get_subscription_service
from api.v1 import error_descriptions as error_texts

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/', response_model=schemas.SubscriptionIn, summary='Create a subscription')
@check_role()
async def create_subscription(
        subscription: schemas.SubscriptionIn,
        user: schemas.User = Depends(JWTBearer()),
        subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Create a subscription:

    - **title**: title to subscription
    - **description**: description to subscription
    - **price**: price to subscription
    """
    try:
        db_subscription = await subscription_service.create_subscription(subscription=subscription)
        return db_subscription
    except IntegrityError as e:
        logger.error(e)
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_texts.duplication_subscription)


@router.patch('/{title}', response_model=schemas.SubscriptionIn, summary='Change a subscription')
@check_role()
async def change_subscription(
        title: str,
        subscription: schemas.SubscriptionIn,
        user: schemas.User = Depends(JWTBearer()),
        subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Change a subscription:

    - **title**: title to subscription
    - **description**: description to subscription
    - **price**: price to subscription
    """

    db_subscription = await subscription_service.get_subscription_by_title(title)
    if not db_subscription:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_texts.subscription_not_found)
    res = await subscription_service.change_subscription(subscription=subscription, title=title)
    return res
