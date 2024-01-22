import os

from celery import Celery
from config import config


def celery_init_app(config_name):
    _celery = Celery()
    _celery.config_from_object(config[config_name])

    _celery.autodiscover_tasks([
        'tasks.test_task',
    ])

    return _celery

celery_app = celery_init_app(os.getenv('FLASK_CONFIG'))
