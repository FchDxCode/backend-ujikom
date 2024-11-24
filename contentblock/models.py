# contentblock/models.py

from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from page.models import Page
import os
from django.conf import settings
from .validators import validate_image_path


class ContentBlock(models.Model):
    """
    Model yang merepresentasikan Blok Konten dalam sistem.
    
    Fields:
        page (ForeignKey): Relasi ke model Page yang terkait dengan blok konten ini.
        title (CharField): Judul blok konten.
        image (ImageField): Gambar terkait dengan blok konten, opsional dengan validasi path gambar.
        description (TextField): Deskripsi blok konten, opsional.
        created_by (ForeignKey): Pengguna yang membuat blok konten.
        updated_at (DateTimeField): Tanggal dan waktu terakhir kali blok konten diperbarui.
        sequence_number (PositiveIntegerField): Nomor urut blok konten untuk penataan.
    """
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='content_blocks')
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='', blank=True, null=True, validators=[validate_image_path])
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    sequence_number = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override method save untuk mengatur path upload gambar dan menyimpan instance.
        
        Args:
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            None
        """
        # Tentukan path folder berdasarkan slug dari page terkait
        if not self.pk:
            self.set_upload_paths()
        super().save(*args, **kwargs)

    def set_upload_paths(self):
        """
        Mengatur path upload untuk field gambar berdasarkan slug dari judul page terkait.
        
        Returns:
            None
        """
        if self.page:
            page_slug = slugify(self.page.title)
            self.image.field.upload_to = f'pages/{page_slug}/images'

    def clean(self):
        """
        Override method clean untuk melakukan validasi tambahan pada field.
        
        Returns:
            None
        """
        super().clean()
        if self.image:
            validate_image_path(self.image)

    def __str__(self):
        """
        Representasi string dari objek ContentBlock, yaitu judul dan judul page terkait.
        
        Returns:
            str: Representasi string dari ContentBlock.
        """
        return f"{self.title} ({self.page.title})"


# Signals for managing sequence_number and folders

@receiver(pre_save, sender=ContentBlock)
def set_contentblock_sequence(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil sebelum ContentBlock disimpan.
    Mengatur sequence_number secara otomatis untuk instance baru.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (ContentBlock): Instance ContentBlock yang akan disimpan.
        **kwargs: Argumen kata kunci tambahan.
    
    Returns:
        None
    """
    if not instance.pk:  # Hanya untuk instance baru
        last_sequence = ContentBlock.objects.filter(page=instance.page).aggregate(models.Max('sequence_number'))['sequence_number__max']
        instance.sequence_number = (last_sequence or 0) + 1


@receiver(post_delete, sender=ContentBlock)
def reorder_contentblock_sequence(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil setelah ContentBlock dihapus.
    Mengatur ulang sequence_number untuk semua ContentBlock dalam page yang sama.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (ContentBlock): Instance ContentBlock yang telah dihapus.
        **kwargs: Argumen kata kunci tambahan.
    
    Returns:
        None
    """
    content_blocks = ContentBlock.objects.filter(page=instance.page).order_by('sequence_number')
    for index, block in enumerate(content_blocks):
        if block.sequence_number != index + 1:
            block.sequence_number = index + 1
            block.save(update_fields=['sequence_number'])
