from app import celery


@celery.task()
def add(x, y):
    result = x + y
    print(result)
    return result
