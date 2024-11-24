# album/serializers.py

from rest_framework import serializers
from .models import Album
import os
from django.conf import settings
from django.utils.text import slugify


class AlbumSerializer(serializers.ModelSerializer):
    """
    Serializer untuk model Album.
    
    Fields:
        id (IntegerField): ID unik album.
        title (CharField): Judul album.
        description (TextField): Deskripsi album, opsional.
        created_at (DateTimeField): Tanggal dan waktu pembuatan album.
        category (PrimaryKeyRelatedField): Kategori yang terkait dengan album.
        created_by (CharField): Username pengguna yang membuat album (read-only).
        folder_path (SerializerMethodField): Path folder fisik album (read-only).
        is_active (BooleanField): Status aktif/inaktif album.
        sequence_number (PositiveIntegerField): Nomor urut album untuk penataan (read-only).
        cover_photo_url (SerializerMethodField): URL foto sampul album (read-only).
    """
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    folder_path = serializers.SerializerMethodField()
    cover_photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Album
        fields = [
            'id', 
            'title', 
            'description', 
            'created_at', 
            'category', 
            'created_by', 
            'folder_path', 
            'is_active',
            'sequence_number', 
            'cover_photo_url'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'created_by', 
            'folder_path', 
            'sequence_number'
        ]
    
    def get_folder_path(self, obj):
        """
        Mendapatkan path folder fisik untuk album.
        
        Args:
            obj (Album): Instance album.
        
        Returns:
            str: Path lengkap ke folder album berdasarkan MEDIA_URL dan judul album.
        """
        return os.path.join(settings.MEDIA_URL, slugify(obj.title))
    
    def get_cover_photo_url(self, obj):
        """
        Mendapatkan URL foto sampul album.
        
        Args:
            obj (Album): Instance album.
        
        Returns:
            str atau None: URL foto sampul jika ada, jika tidak maka None.
        """
        if obj.cover_photo:
            return obj.cover_photo.photo.url
        return None
