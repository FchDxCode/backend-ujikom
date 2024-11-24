# urls.py - Konfigurasi routing untuk view terkait foto

from django.urls import path
from .views import PhotoListCreateView, PhotoDetailView, PhotoByAlbumView, PhotoListPublic, like_photo, PublicPhotoDetailView

# Daftar URL untuk aplikasi foto
urlpatterns = [
    # Endpoint untuk menampilkan daftar semua foto atau membuat foto baru
    path('photos/', PhotoListCreateView.as_view(), name='photo-list-create'),
    
    # Endpoint untuk mengambil, memperbarui, atau menghapus foto tertentu berdasarkan primary key (pk)
    path('photos/<int:pk>/', PhotoDetailView.as_view(), name='photo-detail'),
    
    # Endpoint untuk mengambil daftar foto berdasarkan ID album tertentu
    path('photos/album/<int:album_id>/', PhotoByAlbumView.as_view(), name='photos-by-album'),
    
    # Endpoint untuk menampilkan daftar foto yang bersifat publik saja
    path('photos/public/', PhotoListPublic.as_view(), name='photo-list-public'),
    
    # Endpoint publik untuk detail foto
    path('photos/public/<int:pk>/', PublicPhotoDetailView.as_view(), name='public-photo-detail'),
    
    # Endpoint untuk memberikan "like" pada foto tertentu berdasarkan ID foto
    path('photos/<int:photo_id>/like/', like_photo, name='photo-like'),
]
