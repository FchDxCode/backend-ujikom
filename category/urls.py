# urls.py

from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView, CategoryPublicListView

urlpatterns = [
    # Endpoint untuk mendapatkan daftar semua kategori atau membuat kategori baru
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),  
    
    # Endpoint untuk mendapatkan, memperbarui, atau menghapus kategori tertentu berdasarkan ID (pk)
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Endpoint untuk mendapatkan daftar semua kategori yang bersifat publik
    path('categories/public/', CategoryPublicListView.as_view(), name='category-public-list'),
]
