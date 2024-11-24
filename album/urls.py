# album/urls.py

from django.urls import path
from .views import (
    AlbumListCreateView, 
    AlbumDetailView, 
    PublicAlbumListView, 
    AlbumByCategoryView
)

urlpatterns = [
    # Endpoint untuk mendapatkan daftar semua album atau membuat album baru
    path('albums/', AlbumListCreateView.as_view(), name='album-list-create'),
    
    # Endpoint untuk mendapatkan, memperbarui, atau menghapus album tertentu berdasarkan ID (pk)
    path('albums/<int:pk>/', AlbumDetailView.as_view(), name='album-detail'),
    
    # Endpoint untuk mendapatkan daftar semua album yang bersifat publik
    path('albums/public/', PublicAlbumListView.as_view(), name='public-album-list'),
    
    # Endpoint untuk mendapatkan daftar album berdasarkan kategori tertentu yang diidentifikasi oleh category_id
    path('albums/category/<int:category_id>/', AlbumByCategoryView.as_view(), name='album-by-category'),
]
