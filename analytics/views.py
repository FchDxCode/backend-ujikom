from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from .models import Analytics
from .serializers import AnalyticsStatsSerializer
from gallery.throttles import AdminRateThrottle
from users.permissions import IsAdmin
import logging
from django.http import FileResponse
from django.conf import settings
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Create your views here.

class AnalyticsStatsView(APIView):
    """
    Retrieve analytics statistics.
    
    Endpoint ini menyediakan statistik analytics untuk admin.
    Rate limits:
    - Petugas: 1000 requests/day
    - Admin: 5000 requests/day
    
    Parameters:
        days (int): Jumlah hari untuk analisis data, default 30
        
    Returns:
        {
            "total_views": int,      # Total seluruh request API
            "recent_views": int,      # Total request dalam periode yang ditentukan
            "unique_visitors": int,   # Jumlah pengunjung unik berdasarkan IP
            "successful_requests": int, # Jumlah request sukses (status 2xx)
            "period_days": int        # Periode hari yang dianalisis
        }
        
    Raises:
        ValidationError: Jika parameter days tidak valid
        PermissionDenied: Jika user bukan admin
        Throttled: Jika melewati batas rate limiting
    """
    permission_classes = [IsAdmin]
    throttle_classes = [AdminRateThrottle]

    def get(self, request):
        try:
            days = request.query_params.get('days', 30)
            days = int(days)
            
            cache_key = f'analytics_stats_{days}'
            stats = cache.get(cache_key)
            
            if not stats:
                stats = Analytics.get_stats(days=days)
                cache.set(cache_key, stats, timeout=3600)  # Cache for 1 hour
            
            serializer = AnalyticsStatsSerializer(data=stats)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data)
            
        except ValueError as e:
            logger.warning(f"Invalid days parameter: {request.query_params.get('days')}")
            return Response({"error": "Invalid days parameter"}, status=400)
        except Exception as e:
            logger.error(f"Error retrieving analytics stats: {str(e)}", exc_info=True)
            return Response({"error": "Internal server error"}, status=500)

class AnalyticsArchiveView(APIView):
    """
    View untuk mengakses file arsip analytics.
    Hanya admin yang bisa mengakses.
    """
    permission_classes = [IsAdmin]
    
    def get(self, request, filename=None):
        try:
            # Jika filename tidak ada, tampilkan daftar arsip
            if filename is None:
                archive_dir = os.path.join(settings.MEDIA_ROOT, 'analytics', 'archives')
                files = []
                
                if os.path.exists(archive_dir):
                    for file in os.listdir(archive_dir):
                        if file.endswith('.csv'):
                            filepath = os.path.join(archive_dir, file)
                            files.append({
                                'name': file,
                                'size': os.path.getsize(filepath),
                                'created': datetime.fromtimestamp(os.path.getctime(filepath))
                            })
                
                return Response({
                    'archives': sorted(files, key=lambda x: x['created'], reverse=True)
                })
            
            # Jika filename ada, download file
            filepath = os.path.join(settings.MEDIA_ROOT, 'analytics', 'archives', filename)
            if not os.path.exists(filepath):
                return Response({'error': 'File not found'}, status=404)
                
            return FileResponse(
                open(filepath, 'rb'), 
                as_attachment=True,
                filename=filename
            )
            
        except Exception as e:
            logger.error(f"Error in AnalyticsArchiveView: {str(e)}", exc_info=True)
            return Response({'error': 'Internal server error'}, status=500)
