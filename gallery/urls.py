# urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

# Definisi pola URL utama untuk proyek Django
urlpatterns = [
    # Endpoint untuk panel admin Django
    path('admin/', admin.site.urls),
    
    # Endpoint untuk mendapatkan token JWT (access dan refresh tokens)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Endpoint untuk memperbarui token JWT menggunakan refresh token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Menyertakan URL dari aplikasi 'users' di bawah prefix 'api/'
    path('api/', include('users.urls')),
    
    # Menyertakan URL dari aplikasi 'category' di bawah prefix 'api/'
    path('api/', include('category.urls')),
    
    # Menyertakan URL dari aplikasi 'album' di bawah prefix 'api/'
    path('api/', include('album.urls')),
    
    # Menyertakan URL dari aplikasi 'photo' di bawah prefix 'api/'
    path('api/', include('photo.urls')),
    
    # Menyertakan URL dari aplikasi 'page' di bawah prefix 'api/pages/'
    path('api/pages/', include('page.urls')),
    
    # Menyertakan URL dari aplikasi 'contentblock' di bawah prefix 'api/contentblocks/'
    path('api/contentblocks/', include('contentblock.urls')),
    
    # Menyertakan URL dari aplikasi 'analytics' di bawah prefix 'api/analytics/'
    path('api/analytics/', include('analytics.urls')),
    
    # Menyertakan URL dari aplikasi 'dashboard' di bawah prefix 'api/dashboard/'
    path('api/dashboard/', include('dashboard.urls')),
    
    path('api/assistant/', include('assistant.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Menambahkan URL untuk melayani file media saat mode DEBUG aktif
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
