# page/serializers.py

from rest_framework import serializers
from .models import Page


class PageSerializer(serializers.ModelSerializer):
    """
    Serializer untuk model Page.
    
    Kelas ini digunakan untuk mengubah instance model Page menjadi representasi JSON
    dan sebaliknya. Serializer ini mencakup semua field yang ada dalam model Page.
    
    Fields:
        id (IntegerField): ID unik dari Page (read-only).
        title (CharField): Judul halaman.
        slug (SlugField): Slug yang dihasilkan dari judul halaman.
        content (TextField): Konten utama halaman.
        is_active (BooleanField): Status aktif atau tidaknya halaman.
        created_at (DateTimeField): Tanggal dan waktu pembuatan halaman (read-only).
        updated_at (DateTimeField): Tanggal dan waktu terakhir kali halaman diperbarui (read-only).
        sequence_number (PositiveIntegerField): Nomor urut halaman untuk penataan (read-only).
    """
    
    class Meta:
        """
        Meta kelas untuk konfigurasi serializer.
        
        Attributes:
            model (Model): Model yang diserialisasi adalah Page.
            fields (list atau str): Menentukan field yang akan disertakan dalam serializer.
                                  Dalam hal ini, semua field disertakan menggunakan '__all__'.
        """
        model = Page
        fields = '__all__'
