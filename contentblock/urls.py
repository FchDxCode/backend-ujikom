# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContentBlockViewSet, 
    PublicContentBlockListView, 
    ContentBlockByPages, 
    ContentBlockByPageSlug,
    ContentBlockDetailView
)

# Inisialisasi router DefaultRouter dari Django REST Framework
router = DefaultRouter()
# Mendaftarkan ContentBlockViewSet ke router dengan basename 'contentblock'
router.register(r'', ContentBlockViewSet, basename='contentblock')

urlpatterns = [
    # Endpoint untuk mendapatkan daftar semua ContentBlock yang bersifat publik
    path('public/', PublicContentBlockListView.as_view(), name='public-contentblock-list'),
    
    # Endpoint untuk mendapatkan daftar ContentBlock berdasarkan ID halaman (page_id)
    path('page/<int:page_id>/', ContentBlockByPages.as_view(), name='contentblock-by-pages'),
    
    # Endpoint untuk mendapatkan daftar ContentBlock berdasarkan slug halaman (page_slug)
    path('page/slug/<str:page_slug>/', ContentBlockByPageSlug.as_view(), name='contentblock-by-page-slug'),
    
    # Endpoint untuk mendapatkan detail ContentBlock berdasarkan ID
    path('detail/<int:id>/', ContentBlockDetailView.as_view(), name='contentblock-detail'),
    
    # Menyertakan semua URL yang didefinisikan oleh router
    path('', include(router.urls)),
]
