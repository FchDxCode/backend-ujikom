from django.core.management import call_command
import logging

# Mendapatkan instance logger untuk modul ini
logger = logging.getLogger(__name__)


def verify_contentblock_paths():
    """
    Fungsi untuk memverifikasi dan memperbaiki path pada ContentBlock.

    Fungsi ini memanggil perintah manajemen Django 'fix_contentblock_paths' untuk memastikan
    bahwa semua path gambar pada ContentBlock telah dikonfigurasi dengan benar.
    Jika terjadi kesalahan selama eksekusi perintah, kesalahan tersebut akan dicatat
    menggunakan logger.

    Returns:
        None
    """
    try:
        # Memanggil perintah manajemen 'fix_contentblock_paths'
        call_command('fix_contentblock_paths')
    except Exception as e:
        # Mencatat kesalahan jika terjadi exception selama pemanggilan perintah
        logger.error(f"Error verifying content block paths: {str(e)}")
