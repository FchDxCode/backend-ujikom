# photo/serializers.py

from rest_framework import serializers
from .models import Photo
from django.utils.text import slugify
from django.conf import settings
import os


class PhotoSerializer(serializers.ModelSerializer):
    # Menampilkan username pengguna yang mengupload foto sebagai read-only
    uploaded_by = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Photo
        fields = ['id', 'title', 'description', 'photo', 'album', 'uploaded_at', 'uploaded_by', 'sequence_number', 'likes']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by', 'sequence_number', 'likes']
    
    def get_photo_url(self, obj):
        # Dapatkan folder album saat ini berdasarkan slug nama album
        album_folder = slugify(obj.album.title)
        # Generate path dinamis untuk foto
        photo_path = os.path.join('albums', album_folder, os.path.basename(obj.photo.name))
        # Mengembalikan URL lengkap untuk foto
        return f'{settings.MEDIA_URL}{photo_path}'
    
    def create(self, validated_data):
        # Mengatur pengguna yang mengupload foto berdasarkan konteks permintaan
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        # Validasi jika title atau description kosong, tambahkan default
        if not data.get('title'):
            data['title'] = f"Photo {data['album'].photos.count() + 1}"
        if not data.get('description'):
            data['description'] = "No description provided"
        return data


class MultiplePhotoSerializer(serializers.ListSerializer):
    # Mendefinisikan child serializer sebagai PhotoSerializer
    child = PhotoSerializer()
    
    def create(self, validated_data):
        # Mendapatkan pengguna dari konteks permintaan
        request = self.context.get('request')
        # Membuat instance Photo untuk setiap data yang divalidasi
        photos = [Photo(**item, uploaded_by=request.user) for item in validated_data]
        # Menyimpan semua foto secara massal ke database
        return Photo.objects.bulk_create(photos)
