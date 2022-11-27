import logging
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler

import ecs_logging
from flask import request


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = request.headers.get('X-Request-Id')
        except:
            pass
        return True

dictConfig({
    'version': 1,
    'filters': {
        'request_id_filter': {
            '()': RequestIdFilter
        }
    },
    'formatters': {
        'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'},
        'ecs_logging': {
            '()': ecs_logging.StdlibFormatter,
         }
    },
    'handlers': {
        'default': { 
            'formatter': 'default',
            'class': 'logging.StreamHandler',
        },
        'wsgi': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/app/logs.json',
            'when': 'h',
            'interval': 1, 
            'backupCount': 5,
            'formatter': 'ecs_logging',
            'filters': ['request_id_filter']
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'default']
    }
})