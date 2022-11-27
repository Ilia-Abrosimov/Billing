import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from db.postgres import Base


class Payment(Base):
    __tablename__ = 'payments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    user_id = sqlalchemy.Column(UUID(as_uuid=True), nullable=False, index=True)
    start_date = sqlalchemy.Column(sqlalchemy.DATE, index=True)
    end_date = sqlalchemy.Column(sqlalchemy.DATE, index=True)
    subscription_id = sqlalchemy.Column(sqlalchemy.ForeignKey('subscriptions.id'), index=True)
    payment_url = sqlalchemy.Column(sqlalchemy.String)
    is_paid = sqlalchemy.Column(sqlalchemy.Boolean, index=True, default=False)
    intent_id = sqlalchemy.Column(sqlalchemy.String)
    client_secret = sqlalchemy.Column(sqlalchemy.String)
    subscription = relationship("Subscription", back_populates="payments", uselist=False, lazy="joined")


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    description = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    roles = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.String), nullable=False)
    payments = relationship("Payment", back_populates="subscription")


class Event(Base):
    __tablename__ = 'events'

    payment_system_id = sqlalchemy.Column(sqlalchemy.String)
    received_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        primary_key=True,
        nullable=False,
        server_default=sqlalchemy.text('CURRENT_TIMESTAMP'),
    )
    data = sqlalchemy.Column(JSONB)
    processed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
