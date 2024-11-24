# urls.py - Konfigurasi URL untuk manajemen user, autentikasi, dan registrasi

from django.urls import path
from .views import UserListCreateView, UserDetailView, CustomTokenObtainPairView, RegisterUserView, LogoutView
import logging

logger = logging.getLogger(__name__)

# Daftar URL untuk aplikasi pengguna
urlpatterns = [
    # Endpoint untuk daftar dan pembuatan user
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    
    # Endpoint untuk menampilkan detail, memperbarui, atau menghapus user berdasarkan primary key (pk)
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    
    # Endpoint untuk login dan mendapatkan token autentikasi
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Endpoint untuk registrasi user baru
    path('register/', RegisterUserView.as_view(), name='register-user'),
    
    # Endpoint untuk logout dan mencabut token
    path('logout/', LogoutView.as_view(), name='logout'),
]

logger.debug("URL configuration loaded with login endpoint")
