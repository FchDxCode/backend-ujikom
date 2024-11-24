from django.db import models
from django.utils import timezone
from django.core.cache import cache
import logging
import csv
import os
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class Analytics(models.Model):
    """
    Model untuk mencatat setiap kunjungan ke API publik.
    
    Fields:
        path (CharField): Path URL yang diakses.
        method (CharField): HTTP method yang digunakan (GET, POST, dll).
        timestamp (DateTimeField): Waktu akses.
        ip_address (GenericIPAddressField): Alamat IP pengunjung.
        user_agent (TextField): User agent dari browser/client.
        is_authenticated (BooleanField): Status autentikasi pengunjung.
        response_status (PositiveSmallIntegerField): Status code response (200, 404, dll).
    """
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)  # GET, POST, etc.
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    is_authenticated = models.BooleanField(default=False)
    response_status = models.PositiveSmallIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['path']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.method} {self.path} - {self.timestamp}"

    @classmethod
    def cleanup_old_records(cls, days=90):
        """
        Hapus record analytics yang lebih lama dari X hari.
        
        Args:
            days (int): Jumlah hari untuk menyimpan data
            
        Returns:
            int: Jumlah record yang dihapus
        """
        try:
            cutoff = timezone.now() - timezone.timedelta(days=days)
            deleted_count, _ = cls.objects.filter(timestamp__lt=cutoff).delete()
            logger.info(f"Cleaned up {deleted_count} old analytics records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old records: {str(e)}", exc_info=True)
            raise

    @classmethod
    def get_stats(cls, days=30):
        """
        Mendapatkan statistik view untuk periode tertentu.
        
        Args:
            days (int): Jumlah hari ke belakang untuk statistik.
            
        Returns:
            dict: Dictionary berisi statistik view.
            
        Raises:
            ValueError: Jika days <= 0
        """
        if days <= 0:
            raise ValueError("Days must be greater than 0")

        cache_key = f'analytics_stats_{days}'
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return cached_stats

        try:
            end_date = timezone.now()
            start_date = end_date - timezone.timedelta(days=days)
            
            total_views = cls.objects.count()
            recent_views = cls.objects.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).count()
            
            unique_visitors = cls.objects.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).values('ip_address').distinct().count()
            
            successful_requests = cls.objects.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date,
                response_status__gte=200,
                response_status__lt=300
            ).count()
            
            stats = {
                'total_views': total_views,
                'recent_views': recent_views,
                'unique_visitors': unique_visitors,
                'successful_requests': successful_requests,
                'period_days': days
            }
            
            cache.set(cache_key, stats, timeout=3600)  # Cache for 1 hour
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating analytics stats: {str(e)}", exc_info=True)
            raise

    @classmethod
    def archive_old_records(cls, days=30):
        """
        Arsipkan record lama ke CSV dan hapus dari database
        """
        try:
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            old_records = cls.objects.filter(timestamp__lt=cutoff_date)
            
            if not old_records.exists():
                return 0

            # Buat direktori archive jika belum ada
            archive_dir = os.path.join(settings.MEDIA_ROOT, 'analytics', 'archives')
            os.makedirs(archive_dir, exist_ok=True)
            
            # Buat nama file dengan timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'analytics_archive_{timestamp}.csv'
            filepath = os.path.join(archive_dir, filename)
            
            # Tulis ke CSV
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Tulis header
                writer.writerow(['path', 'method', 'timestamp', 'ip_address', 
                               'user_agent', 'is_authenticated', 'response_status'])
                
                # Tulis records
                for record in old_records.iterator():
                    writer.writerow([
                        record.path,
                        record.method,
                        record.timestamp.isoformat(),
                        record.ip_address,
                        record.user_agent,
                        record.is_authenticated,
                        record.response_status
                    ])
            
            # Hapus records yang sudah diarsipkan
            deleted_count = old_records.count()
            old_records.delete()
            
            logger.info(f"Archived {deleted_count} records to {filename}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error archiving records: {str(e)}", exc_info=True)
            raise
