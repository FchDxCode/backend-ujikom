# page/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PageViewSet, PublicPageView, PublicPageDetailView

# Inisialisasi router DefaultRouter dari Django REST Framework
router = DefaultRouter()
# Mendaftarkan PageViewSet ke router dengan basename 'pages'
router.register(r'', PageViewSet, basename='pages')

# Definisi pola URL untuk aplikasi 'page'
urlpatterns = [
    # Endpoint untuk mendapatkan daftar semua halaman yang bersifat publik
    path('public/', PublicPageView.as_view(), name='public-pages'),
    
    # Endpoint untuk mendapatkan detail halaman publik berdasarkan slug
    path('public/<str:slug>/', PublicPageDetailView.as_view(), name='public-page-detail'),
    
    # Menyertakan semua URL yang didefinisikan oleh router untuk PageViewSet
    path('', include(router.urls)),
]
