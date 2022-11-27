import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from api.v1 import error_descriptions as error_texts
from api.v1 import schemas
from schema.payment import RefundReason
from services.auth import JWTBearer, check_role
from services.payment import PaymentService, get_payment_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/', summary='Create a refund')
@check_role()
async def create_refund(
        payment: schemas.PaymentIntent,
        user: schemas.User = Depends(JWTBearer()),
        payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Create a refund for payment (can make only admins):

    - **user_id**: user id
    - **intent_id**: intent id
    """

    db_payment = await payment_service.get_payment_by_intent_id(
        user_id=str(payment.user_id),
        intent_id=payment.intent_id,
    )
    if not db_payment:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_texts.no_payment)

    refund = await payment_service.add_new_refund(
        payment_intent=payment.intent_id,
        reason=RefundReason.requested_by_customer.name,
        idempotency_key=payment.intent_id
    )

    return JSONResponse(status_code=HTTPStatus.OK, content='OK')
