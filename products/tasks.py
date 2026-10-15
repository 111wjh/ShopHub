
from celery import shared_task


@shared_task
def test_celery_task():
    return "ShopHub Celery task executed successfully!"
