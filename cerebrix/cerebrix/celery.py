import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cerebrix.settings')

app = Celery('cerebrix')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


def get_celery_worker_status():
    i = app.control.inspect()
    availability = i.ping() 
    result = {
        'availability': availability, 
    }
    return result