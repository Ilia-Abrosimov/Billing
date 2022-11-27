import uvicorn
import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import payments, subscriptions, refunds, webhook
from core.config import settings
from ecom import abstract, event_listeners, stripe_api

sentry_sdk.init(
    dsn=settings.sentry.dsn,
    traces_sample_rate=settings.sentry.traces_sample_rate,
)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    abstract.api_client = stripe_api.StripeClient(
        secret_key=settings.stripe.secret_key.get_secret_value(),
        method_types=settings.payment.method_types,
        public_key=settings.stripe.public_key.get_secret_value(),
    )
    event_listeners.event_listener = event_listeners.StripeEventListener(
        endpoint_secret=settings.stripe.endpoint_secret.get_secret_value())


@app.on_event('shutdown')
async def shutdown():
    ...


app.include_router(payments.router, prefix='/api/v1/payments', tags=['payments'])
app.include_router(subscriptions.router, prefix='/api/v1/subscriptions', tags=['subscriptions'])
app.include_router(refunds.router, prefix='/api/v1/refunds', tags=['refunds'])
app.include_router(webhook.router, prefix='/api/v1/webhook', tags=['webhook'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=settings.uvicorn_reload,
        host='0.0.0.0',
        port=4242,
    )
