from http import HTTPStatus

import pytest

import testdata.data
from settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_add_payment_by_user(make_post_request):
    subscription = testdata.data.subscription
    headers = {f'Authorization': f'Bearer {testdata.data.superadmin_token}'}
    response = await make_post_request(
        endpoint=f'{test_settings.subscriptions_router_prefix}',
        body=subscription.__dict__,
        headers=headers
    )
    assert response.status == HTTPStatus.OK
    assert response.body == subscription.__dict__

    payment = testdata.data.payment
    headers = {f'Authorization': f'Bearer {testdata.data.user_token}'}
    response = await make_post_request(
        endpoint=f'{test_settings.payments_router_prefix}',
        body=payment.__dict__,
        headers=headers
    )
    assert response.status == HTTPStatus.OK
