from .models import Analytics
from rest_framework.permissions import AllowAny
from django.urls import resolve
import logging

logger = logging.getLogger(__name__)

class AnalyticsMiddleware:
    """
    Middleware untuk mencatat setiap request API ke dalam Analytics.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.path.startswith('/api/') and 
            not request.path.startswith('/api/analytics/') and
            not request.path.startswith('/api/dashboard/')):
            
            try:
                # Cek permission class dari view
                resolved = resolve(request.path)
                view_func = resolved.func
                
                # Periksa apakah view adalah class-based atau function-based
                if hasattr(view_func, 'cls'):
                    # Class-based view
                    permission_classes = getattr(view_func.cls, 'permission_classes', [])
                elif hasattr(view_func, 'view_class'):
                    # Class-based view (alternatif)
                    permission_classes = getattr(view_func.view_class, 'permission_classes', [])
                else:
                    # Function-based view
                    permission_classes = getattr(view_func, 'permission_classes', [])

                # Periksa apakah view menggunakan AllowAny permission
                is_public_api = any(issubclass(permission, AllowAny) for permission in permission_classes)

                # Hanya catat jika API bersifat public (AllowAny)
                if is_public_api:
                    Analytics.objects.create(
                        path=request.path,
                        method=request.method,
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT'),
                        is_authenticated=request.user.is_authenticated,
                        response_status=response.status_code
                    )

            except Exception as e:
                logger.error(
                    f"Error recording analytics: {str(e)}", 
                    extra={
                        'path': request.path,
                        'method': request.method,
                        'status_code': response.status_code
                    },
                    exc_info=True
                )

        return response

    def get_client_ip(self, request):
        """
        Mendapatkan IP address client dengan mempertimbangkan proxy.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
