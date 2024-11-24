# page/models.py

from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .utils import rename_page_folder, create_page_folder, delete_page_folder


class Page(models.Model):
    """
    Model yang merepresentasikan Halaman dalam sistem.
    
    Fields:
        title (CharField): Judul halaman yang unik.
        slug (SlugField): Slug yang dihasilkan dari judul halaman, unik dan opsional.
        content (TextField): Konten utama halaman.
        is_active (BooleanField): Status aktif atau tidaknya halaman.
        created_at (DateTimeField): Tanggal dan waktu pembuatan halaman.
        updated_at (DateTimeField): Tanggal dan waktu terakhir kali halaman diperbarui.
        sequence_number (PositiveIntegerField): Nomor urut halaman untuk penataan.
    """
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    content = models.TextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sequence_number = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override method save untuk mengatur slug dan mengelola folder halaman.
        
        Jika slug belum diatur atau slug tidak sesuai dengan slug dari judul,
        maka slug akan diperbarui dan folder halaman akan dibuat atau diubah namanya
        sesuai dengan slug baru.
        
        Args:
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            None
        """
        # Cek apakah slug perlu diperbarui
        if not self.slug or slugify(self.title) != self.slug:
            old_slug = self.slug  # Simpan slug lama sebelum diperbarui
            self.slug = slugify(self.title)  # Perbarui slug berdasarkan judul
            
            super().save(*args, **kwargs)  # Simpan instance terlebih dahulu
            
            if old_slug:
                # Jika ada slug lama, ganti nama folder halaman
                rename_page_folder(old_slug, self.slug)
            else:
                # Jika tidak ada slug lama, buat folder halaman baru
                create_page_folder(self.slug)
        else:
            super().save(*args, **kwargs)  # Simpan instance tanpa perubahan slug

    def delete(self, *args, **kwargs):
        """
        Override method delete untuk menghapus folder halaman sebelum menghapus instance.
        
        Args:
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            None
        """
        delete_page_folder(self.slug)  # Hapus folder halaman terkait
        super().delete(*args, **kwargs)  # Hapus instance

    def __str__(self):
        """
        Representasi string dari objek Page, yaitu judul halaman.
        
        Returns:
            str: Judul halaman.
        """
        return self.title


# Signal untuk mengatur sequence_number sebelum menyimpan halaman baru
@receiver(pre_save, sender=Page)
def set_sequence_number(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil sebelum Page disimpan.
    Mengatur sequence_number secara otomatis untuk instance baru.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Page): Instance Page yang akan disimpan.
        **kwargs: Argumen kata kunci tambahan.
    
    Returns:
        None
    """
    if not instance.pk:  # Hanya untuk instance baru
        last_sequence = Page.objects.aggregate(models.Max('sequence_number'))['sequence_number__max']
        instance.sequence_number = (last_sequence or 0) + 1


# Signal untuk mengatur ulang sequence_number setelah menghapus halaman
@receiver(post_delete, sender=Page)
def reorder_sequence_numbers(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil setelah Page dihapus.
    Mengatur ulang sequence_number untuk semua Page dalam urutan yang benar.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Page): Instance Page yang telah dihapus.
        **kwargs: Argumen kata kunci tambahan.
    
    Returns:
        None
    """
    pages = Page.objects.order_by('sequence_number')  # Ambil semua halaman terurut berdasarkan sequence_number
    for index, page in enumerate(pages):
        if page.sequence_number != index + 1:
            page.sequence_number = index + 1  # Perbarui sequence_number agar berurutan
            page.save(update_fields=['sequence_number'])  # Simpan perubahan pada sequence_number
