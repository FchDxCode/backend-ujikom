# serializers.py

from rest_framework import serializers
from .models import ContentBlock


class ContentBlockSerializer(serializers.ModelSerializer):
    """
    Serializer untuk model ContentBlock.
    
    Fields:
        id (IntegerField): ID unik ContentBlock (read-only).
        page (PrimaryKeyRelatedField): Relasi ke model Page yang terkait dengan ContentBlock.
        title (CharField): Judul ContentBlock.
        image (ImageField): Gambar terkait dengan ContentBlock, opsional.
        description (TextField): Deskripsi ContentBlock, opsional.
        created_by (CharField): Username pengguna yang membuat ContentBlock (read-only).
        sequence_number (PositiveIntegerField): Nomor urut ContentBlock untuk penataan (read-only).
        updated_at (DateTimeField): Tanggal dan waktu terakhir kali ContentBlock diperbarui (read-only).
    """
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ContentBlock
        fields = [
            'id', 
            'page', 
            'title', 
            'image', 
            'description', 
            'created_by', 
            'sequence_number', 
            'updated_at'
        ]
        read_only_fields = [
            'sequence_number', 
            'updated_at', 
            'created_by'
        ]
