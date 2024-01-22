from .. import celery_app


@celery_app.task()
def add(x, y):
    print('Hello job add')
    result = x + y
    return result
