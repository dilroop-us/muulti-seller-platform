import os
from celery import Celery
from decouple import config

# Set default settings for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PixelDojo.settings")

app = Celery("PixelDojo")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
