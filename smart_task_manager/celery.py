import os
from celery import Celery
import logging

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_task_manager.settings')

app = Celery('smart_task_manager')

# قراءة إعدادات Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# اكتشاف المهام تلقائيًا من جميع التطبيقات
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.debug(f'Request: {self.request!r}')
