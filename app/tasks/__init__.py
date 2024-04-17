from celery import Celery
from config import config


def celery_init_app(name, config_name):
    _celery = Celery(name)
    _celery.config_from_object(config[config_name])

    _celery.autodiscover_tasks([
        'app.tasks.feed_task',
        'app.tasks.test_task'
    ])

    return _celery
