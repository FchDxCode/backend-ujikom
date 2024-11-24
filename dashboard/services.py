from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from users.models import User
from category.models import Category
from album.models import Album
from photo.models import Photo
from page.models import Page
from contentblock.models import ContentBlock
from analytics.models import Analytics

class DashboardService:
    @staticmethod
    def get_model_stats(model, active_field=None):
        """
        Mendapatkan statistik dasar untuk model tertentu
        """
        stats = {
            'total': model.objects.count()
        }
        
        if active_field:
            stats.update({
                'active': model.objects.filter(**{active_field: True}).count(),
                'inactive': model.objects.filter(**{active_field: False}).count()
            })
            
        return stats

    @classmethod
    def get_dashboard_stats(cls):
        """
        Mengumpulkan semua statistik untuk dashboard
        """
        return {
            'users': {
                'total': User.objects.count(),
                'admin': User.objects.filter(role='admin').count(),
                'petugas': User.objects.filter(role='petugas').count()
            },
            'categories': cls.get_model_stats(Category),
            'albums': cls.get_model_stats(Album, 'is_active'),
            'photos': cls.get_model_stats(Photo),
            'pages': cls.get_model_stats(Page, 'is_active'),
            'content_blocks': cls.get_model_stats(ContentBlock),
            'analytics': Analytics.get_stats(days=30)  # Menggunakan method yang sudah ada
        }
