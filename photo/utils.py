# utils.py - Modul utilitas untuk operasi terkait foto

import os
from django.utils.text import slugify
from django.conf import settings
from album.models import Album
import hashlib
import time

def refresh_photo_paths():
    """
    Memperbarui path foto berdasarkan struktur album.
    
    Mengambil semua objek foto dari database dan memastikan bahwa setiap file foto
    dipindahkan ke folder yang sesuai berdasarkan nama album. Jika path file foto
    berubah, path baru tersebut juga disimpan ke dalam database.
    
    Proses:
    1. Ambil semua foto dari model `Photo`.
    2. Tentukan path lama dan path baru berdasarkan struktur album.
    3. Jika file ada di lokasi lama, pindahkan ke lokasi baru yang telah ditentukan.
    4. Perbarui path file foto di database untuk menyimpan lokasi baru.
    
    Menggunakan:
    - `Photo`: Model untuk foto yang memiliki informasi album terkait.
    - `settings.MEDIA_ROOT`: Root direktori media untuk file foto.
    - `slugify`: Untuk membuat slug berdasarkan judul album sehingga path lebih konsisten.
    """
    
    from photo.models import Photo  # Mengimpor model Photo
    photos = Photo.objects.all()  # Mengambil semua objek foto dari database

    for photo in photos:
        album = photo.album
        old_photo_path = os.path.join(settings.MEDIA_ROOT, photo.photo.name)  # Path lama yang disimpan di database
        new_folder = os.path.join(settings.MEDIA_ROOT, 'albums', slugify(album.title))  # Path folder baru berdasarkan album
        new_photo_path = os.path.join(new_folder, os.path.basename(photo.photo.name))  # Path file foto baru

        # Pindahkan file dari path lama ke path baru jika ada
        if os.path.exists(old_photo_path) and not os.path.exists(new_photo_path):
            os.rename(old_photo_path, new_photo_path)

        # Perbarui path di database ke path baru yang relatif
        relative_new_photo_path = os.path.join('albums', slugify(album.title), os.path.basename(photo.photo.name))
        photo.photo.name = relative_new_photo_path  # Menyimpan path baru di database
        photo.save()

def hash_filename(filename):
    """
    Membuat nama file unik menggunakan hash.
    
    Menghasilkan nama file yang di-hash berdasarkan timestamp saat ini, 
    memastikan nama file yang dihasilkan unik. Ekstensi asli file tetap dipertahankan.
    
    Proses:
    1. Ekstraksi nama dan ekstensi file.
    2. Membuat hash MD5 berdasarkan timestamp saat ini.
    3. Menggabungkan hash dengan ekstensi asli untuk menghasilkan nama file baru.
    
    Parameter:
    - `filename`: Nama file asli yang ingin di-hash.
    
    Mengembalikan:
    - Nama file baru dengan hash yang mempertahankan ekstensi asli.
    
    Contoh:
    `image.jpg` dapat berubah menjadi `d41d8cd98f00b204e9800998ecf8427e.jpg`.
    """
    
    # Mendapatkan ekstensi file
    name, ext = os.path.splitext(filename)
    # Membuat hash dari timestamp saat ini
    timestamp = str(time.time()).encode('utf-8')
    hashed = hashlib.md5(timestamp).hexdigest()
    # Mengembalikan nama file baru dengan hash dan ekstensi asli
    return f"{hashed}{ext}"
