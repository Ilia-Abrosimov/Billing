import json

import requests
from celery import Celery
from celery.schedules import crontab
from src.core.config import notification_setting, redis_setting
from src.services.subscriptions import get_expiring_subscriptions

celery = Celery('tasks', broker=f'redis://{redis_setting.host}:{redis_setting.port}')


@celery.task
def send_notifications():
    """
    Отправка users_id в сервис notifications для отправки уведомлений об окончании подписки
    """
    expiring_subscriptions = get_expiring_subscriptions()
    users_id = [data.user_id for data in expiring_subscriptions]
    requests.post(notification_setting.dsn,
                  data=json.dumps({'users': users_id, 'event': 'test', 'data': {}}))
    return 'done!'


@celery.on_after_configure.connect
def setup_scheduler_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=10, minute=32),  # Время указывается по UTC
        send_notifications.s(),
        name='Send notifications about expiring subscriptions',
    )
