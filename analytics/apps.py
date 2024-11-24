from django.apps import AppConfig
import os
from django.conf import settings


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def ready(self):
        # Buat direktori untuk arsip analytics
        archive_dir = os.path.join(settings.MEDIA_ROOT, 'analytics', 'archives')
        os.makedirs(archive_dir, exist_ok=True)
