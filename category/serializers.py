# serializers.py

from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer untuk model Category.
    
    Fields:
        id (IntegerField): ID unik kategori (read-only).
        name (CharField): Nama kategori yang unik.
        description (TextField): Deskripsi kategori, opsional.
        sequence_number (PositiveIntegerField): Nomor urut kategori untuk penataan (read-only).
    """
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'sequence_number', 'updated_at']
        read_only_fields = ['id', 'sequence_number', 'updated_at']
