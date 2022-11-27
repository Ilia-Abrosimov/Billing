from enum import Enum


class RefundReason(Enum):
    duplicate = 'Duplicate'
    fraudulent = 'Fraud'
    requested_by_customer = 'Requested'


class CancelReason(Enum):
    duplicate = 'Duplicate'
    fraudulent = 'Fraud'
    abandoned = 'Abandoned'
