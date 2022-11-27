import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse

from api.v1 import schemas
from api.v1 import error_descriptions as error_texts
from api.v1.paginator import Paginator
from api.v1.schemas import AutoPayment
from core.config import settings
from schema.product import Product, ProductData
from services.auth import JWTBearer
from services.payment import PaymentService, get_payment_service
from services.subscruption import SubscriptionService, get_subscription_service
from services.user import UserService, get_user_service

logger = logging.getLogger(__name__)
router = APIRouter()

templates = Jinja2Templates(directory='templates')


@router.post('/', response_model=schemas.ClientSecret, summary='Create a payment')
async def create_payment(
        request: Request,
        payment: schemas.Payment,
        user: schemas.User = Depends(JWTBearer()),
        payment_service: PaymentService = Depends(get_payment_service),
        subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Create a payment for subscription and return url for payment by user:

    - **subscription**: subscription title
    - **start_date**: date of start subscription
    """
    db_payment = await payment_service.get_payment(
        user_id=str(user.id),
        subscription=payment.subscription,
        start_date=payment.start_date
    )
    if db_payment:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_texts.payment_period_not_over)

    subscription = await subscription_service.get_subscription_by_title(payment.subscription)
    if not subscription:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_texts.subscription_not_found)

    product = Product(
        unit_amount=subscription.price,
        currency='usd',
        product_data=ProductData(name=subscription.title, description=subscription.description)
    )

    new_db_payment = await payment_service.add_new_payment(payment, product, user, subscription.id)

    if not settings.debug:
        return schemas.ClientSecret(data=new_db_payment.client_secret)
    else:
        return templates.TemplateResponse(
            'checkout.html',
            {
                'request': request,
                'CLIENT_SECRET': new_db_payment.client_secret,
                'SUBMIT_CAPTION': f'Pay {product.unit_amount / 100} {product.currency}'
            }
        )


@router.get('/', response_model=schemas.PaymentOutSchema, summary='Get paid payments')
async def get_paid_payments(
        user: schemas.User = Depends(JWTBearer()),
        paginator: Paginator = Depends(),
        payment_service: PaymentService = Depends(get_payment_service),
):
    """
        Return paid payments by user:
        - **page[size]**: size of page
        - **page[number]**: number of page
        """
    db_payments = await payment_service.get_paid_payments(
        offset=paginator.page - 1,
        limit=paginator.per_page,
        user_id=str(user.id),
    )

    return schemas.PaymentOutSchema(
        meta=schemas.Pagination(
            page=paginator.page,
            per_page=paginator.per_page,
        ),
        data=[schemas.PaymentOut(**db_payment.__dict__) for db_payment in db_payments],
    )


@router.patch('/auto_payment', summary='Change auto payment')
async def change_auto_payment(
        auto_payment: AutoPayment,
        user: schemas.User = Depends(JWTBearer()),
        user_service: UserService = Depends(get_user_service),
):
    """
        Return paid payments by user:
        - **is_enable**: enable or disable auto payment
        """
    db_user = await user_service.get_user(user.id)
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_texts.no_user)
    await user_service.change_user_is_recurrent_payments(db_user, auto_payment.is_enable)

    return JSONResponse(status_code=HTTPStatus.OK, content='OK')
