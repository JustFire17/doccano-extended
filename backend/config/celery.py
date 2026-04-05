import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(related_name="celery_tasks")

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-voting-end-dates': {
        'task': 'projects.tasks.check_voting_end_dates',
        'schedule': crontab(minute='*'),  # Run every minute
    },
}
