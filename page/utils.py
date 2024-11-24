# page/utils.py

import os
import shutil
from django.conf import settings


def create_page_folder(slug):
    """
    Membuat folder untuk halaman berdasarkan slug yang diberikan.

    Fungsi ini membuat direktori untuk halaman di dalam direktori 'pages' pada MEDIA_ROOT.
    Jika direktori sudah ada, tidak ada tindakan yang diambil.

    Args:
        slug (str): Slug dari halaman yang akan dibuat foldernya.

    Returns:
        str: Path lengkap dari folder yang dibuat.
    """
    folder_path = os.path.join(settings.MEDIA_ROOT, 'pages', slug)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def rename_page_folder(old_slug, new_slug):
    """
    Mengganti nama folder halaman saat slug halaman berubah.

    Fungsi ini mengganti nama direktori halaman dari `old_slug` ke `new_slug`.
    Jika direktori lama tidak ada, tidak ada tindakan yang diambil.

    Args:
        old_slug (str): Slug lama dari halaman.
        new_slug (str): Slug baru dari halaman.

    Returns:
        None
    """
    old_folder_path = os.path.join(settings.MEDIA_ROOT, 'pages', old_slug)
    new_folder_path = os.path.join(settings.MEDIA_ROOT, 'pages', new_slug)
    if os.path.exists(old_folder_path):
        os.rename(old_folder_path, new_folder_path)


def delete_page_folder(slug):
    """
    Menghapus folder halaman beserta seluruh isinya berdasarkan slug yang diberikan.

    Fungsi ini menghapus direktori halaman dari MEDIA_ROOT jika direktori tersebut ada.
    Menggunakan `shutil.rmtree` untuk menghapus folder dan semua isinya secara rekursif.

    Args:
        slug (str): Slug dari halaman yang akan dihapus foldernya.

    Returns:
        None
    """
    folder_path = os.path.join(settings.MEDIA_ROOT, 'pages', slug)
    if os.path.exists(folder_path):
        # Menghapus folder beserta seluruh isinya
        shutil.rmtree(folder_path)  # Menghapus folder dan semua isinya
