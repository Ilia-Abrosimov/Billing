from datetime import datetime

from sqlalchemy import and_
from src.core.config import db_settings
from src.db.postgres import session
from src.models.models import Payment, Subscription


def get_expiring_subscriptions():
    subscriptions = session.query(
        Payment.user_id,
        Payment.end_date,
        Subscription.title).filter(and_(Payment.is_paid == True,
                                        Payment.end_date - datetime.now().date() == db_settings.information_period)).outerjoin(Subscription)
    return subscriptions
