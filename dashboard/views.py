from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import IsAdmin
from django.core.cache import cache
from django.conf import settings
import logging

from .services import DashboardService
from .serializers import DashboardStatsSerializer
from gallery.throttles import AdminRateThrottle

logger = logging.getLogger(__name__)

class DashboardStatsView(APIView):
    """
    API endpoint untuk mendapatkan statistik dashboard.
    
    Menyediakan rangkuman statistik dari seluruh sistem termasuk:
    - Statistik User (admin/petugas)
    - Statistik Konten (kategori, album, foto)
    - Statistik Halaman (pages, content blocks)
    - Statistik Analytics (kunjungan, visitors)

    Permissions:
    - Harus terautentikasi
    - Harus memiliki role admin
    
    Rate Limiting:
    - Admin: 5000 requests/day
    - Petugas: 1000 requests/day
    """
    permission_classes = [IsAdmin]
    throttle_classes = [AdminRateThrottle]
    
    def get(self, request):
        """
        Mengambil statistik dashboard.
        
        Query Parameters:
            refresh (bool): Jika True, akan melewati cache
            
        Returns:
            Response: JSON response berisi statistik dashboard
            
        Raises:
            500: Jika terjadi kesalahan dalam mengambil data
        """
        try:
            # Check if refresh is requested
            should_refresh = request.query_params.get('refresh', '').lower() == 'true'
            
            # Try to get from cache first
            cache_key = 'dashboard_stats'
            if not should_refresh:
                cached_stats = cache.get(cache_key)
                if cached_stats:
                    return Response(cached_stats)
            
            # Get fresh stats
            stats = DashboardService.get_dashboard_stats()
            
            # Validate with serializer
            serializer = DashboardStatsSerializer(data=stats)
            serializer.is_valid(raise_exception=True)
            
            # Cache the validated data
            cache.set(cache_key, serializer.validated_data, timeout=settings.DASHBOARD_CACHE_TIMEOUT)
            
            logger.info(
                "Dashboard stats retrieved successfully",
                extra={
                    'user_id': request.user.id,
                    'refresh': should_refresh
                }
            )
            
            return Response(serializer.validated_data)
            
        except Exception as e:
            logger.error(
                f"Error retrieving dashboard stats: {str(e)}",
                exc_info=True,
                extra={
                    'user_id': request.user.id
                }
            )
            return Response(
                {'error': 'Internal server error occurred'},
                status=500
            )
