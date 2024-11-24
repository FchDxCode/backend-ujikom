import os, uuid
from django.conf import settings
import logging

# Mendapatkan instance logger untuk modul ini
logger = logging.getLogger(__name__)


def create_contentblock_folders(page_slug):
    """
    Membuat folder untuk ContentBlock berdasarkan slug dari halaman terkait.

    Fungsi ini membuat direktori 'images' di dalam direktori halaman yang diidentifikasi oleh `page_slug`.
    Jika direktori sudah ada, tidak ada tindakan yang diambil.

    Args:
        page_slug (str): Slug dari halaman yang terkait dengan ContentBlock.

    Returns:
        None
    """
    image_folder = os.path.join(settings.MEDIA_ROOT, 'pages', page_slug, 'images')
    os.makedirs(image_folder, exist_ok=True)


def rename_contentblock_folders(old_slug, new_slug):
    """
    Mengganti nama folder ContentBlock saat slug halaman berubah.

    Fungsi ini mengganti nama direktori 'images' dari `old_slug` ke `new_slug`.
    Jika direktori lama tidak ada, tidak ada tindakan yang diambil.

    Args:
        old_slug (str): Slug lama dari halaman.
        new_slug (str): Slug baru dari halaman.

    Returns:
        None
    """
    base_path = os.path.join(settings.MEDIA_ROOT, 'pages')
    old_image_folder = os.path.join(base_path, old_slug, 'images')
    new_image_folder = os.path.join(base_path, new_slug, 'images')

    if os.path.exists(old_image_folder):
        os.rename(old_image_folder, new_image_folder)


def generate_random_filename(extension):
    """
    Menghasilkan nama file acak dengan ekstensi yang diberikan.

    Fungsi ini menggunakan UUID untuk memastikan nama file unik.

    Args:
        extension (str): Ekstensi file (misalnya, '.jpg', '.png').

    Returns:
        str: Nama file acak dengan ekstensi yang diberikan.
    """
    return f"{uuid.uuid4().hex}{extension}"


def generate_unique_filename(filepath):
    """
    Menghasilkan nama file unik yang belum ada di sistem.

    Fungsi ini memastikan bahwa nama file yang dihasilkan tidak bentrok dengan file yang sudah ada.

    Args:
        filepath (str): Path lengkap dari file.

    Returns:
        str: Path lengkap dengan nama file unik.
    """
    base, extension = os.path.splitext(filepath)
    unique_filename = generate_random_filename(extension)
    unique_filepath = os.path.join(os.path.dirname(filepath), unique_filename)
    
    while os.path.exists(unique_filepath):
        unique_filename = generate_random_filename(extension)
        unique_filepath = os.path.join(os.path.dirname(filepath), unique_filename)
    
    return unique_filepath


def refresh_contentblock_paths(contentblock, new_slug):
    """
    Memperbarui path gambar untuk ContentBlock setelah perubahan slug halaman.

    Fungsi ini memindahkan file gambar ke direktori baru berdasarkan `new_slug` dan memperbarui field `image` pada ContentBlock.

    Args:
        contentblock (ContentBlock): Instance ContentBlock yang akan diperbarui.
        new_slug (str): Slug baru dari halaman terkait.

    Returns:
        None
    """
    if contentblock.image:
        # Mendapatkan nama file saja
        filename = os.path.basename(contentblock.image.name)
        
        # Membuat path relatif baru
        new_relative_path = os.path.join('pages', new_slug, 'images', filename)
        new_full_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)
        
        # Membuat direktori jika belum ada
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        
        # Jika file ada di lokasi lama, pindahkan ke lokasi baru
        if hasattr(contentblock.image, 'path') and os.path.isfile(contentblock.image.path):
            old_path = contentblock.image.path
            if old_path != new_full_path:
                os.rename(old_path, new_full_path)
        
        # Memperbarui field image dengan path baru
        contentblock.image.name = new_relative_path
        contentblock.save(update_fields=['image'])
        logger.info(
            f"Updated path for ContentBlock {contentblock.id}: "
            f"from {contentblock.image.name} to {new_relative_path}"
        )


def delete_contentblock_files(contentblock):
    """
    Menghapus file gambar terkait dengan ContentBlock.

    Fungsi ini menghapus file gambar dari sistem file jika ada.

    Args:
        contentblock (ContentBlock): Instance ContentBlock yang file gambarnya akan dihapus.

    Returns:
        None
    """
    if contentblock.image and os.path.isfile(contentblock.image.path):
        os.remove(contentblock.image.path)
