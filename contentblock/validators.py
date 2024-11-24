# validators.py

from django.core.exceptions import ValidationError
import os
from django.conf import settings
from django.utils.text import slugify


def validate_image_path(value):
    """
    Validasi path gambar untuk memastikan mengikuti format yang ditentukan.

    Fungsi ini memeriksa apakah path gambar berada dalam format yang diharapkan:
    'pages/<page-slug>/images/<filename>'. Jika path tidak sesuai, akan
    mengangkat ValidationError. Validasi ini hanya diterapkan untuk file yang
    sudah ada (bukan file baru yang diupload).

    Args:
        value (str atau InMemoryUploadedFile): Path gambar yang akan divalidasi.

    Raises:
        ValidationError: Jika path gambar tidak mengikuti format yang ditentukan.
    """
    if not value:
        # Jika tidak ada nilai yang diberikan, lewati validasi
        return
        
    # Memeriksa apakah path mengikuti format yang diharapkan
    path_parts = str(value).split('/')
    
    # Jika file baru diupload, InMemoryUploadedFile tidak akan memiliki path yang sesuai format
    # Jadi kita skip validasi untuk file baru
    if hasattr(value, 'temporary_file_path'):
        return
        
    # Hanya validasi path untuk file yang sudah ada
    if len(path_parts) >= 2:  # Memperbolehkan file baru yang belum memiliki path lengkap
        if path_parts[0] != 'pages' or 'images' not in path_parts:
            raise ValidationError('Image path does not follow the required format: pages/<page-slug>/images/<filename>')
