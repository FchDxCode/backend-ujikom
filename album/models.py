# album/models.py

import os
import shutil
from django.db import models
from django.db.models import Max
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.conf import settings
from users.models import User
from category.models import Category


class Album(models.Model):
    """
    Model yang merepresentasikan Album dalam sistem.
    
    Fields:
        title (CharField): Judul album.
        description (TextField): Deskripsi album, opsional.
        is_active (BooleanField): Status aktif/inaktif album.
        created_at (DateTimeField): Tanggal dan waktu pembuatan album.
        category (ForeignKey): Kategori yang terkait dengan album.
        created_by (ForeignKey): Pengguna yang membuat album.
        sequence_number (PositiveIntegerField): Nomor urut album untuk penataan.
        cover_photo (ForeignKey): Foto sampul album, opsional.
    """
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    sequence_number = models.PositiveIntegerField(blank=True, null=True)
    cover_photo = models.ForeignKey(
        'photo.Photo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='album_cover'
    )

    def save(self, *args, **kwargs):
        """
        Override method save untuk mengatur sequence_number secara otomatis
        saat album baru ditambahkan.
        """
        if self._state.adding:  # Jika album baru ditambahkan
            max_sequence_number = Album.objects.aggregate(max_seq=Max('sequence_number'))['max_seq']
            if max_sequence_number is not None:
                self.sequence_number = max_sequence_number + 1
            else:
                self.sequence_number = 1
        super(Album, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override method delete untuk memastikan sequence_number diubah
        setelah penghapusan album.
        """
        super(Album, self).delete(*args, **kwargs)
        self.restructure_sequence_numbers()

    @staticmethod
    def restructure_sequence_numbers():
        """
        Metode statis untuk mengatur ulang sequence_number semua album
        setelah terjadi penghapusan, memastikan urutan yang konsisten.
        """
        albums = Album.objects.all().order_by('sequence_number')
        for index, album in enumerate(albums, start=1):
            album.sequence_number = index
            album.save()

    def __str__(self):
        """
        Representasi string dari objek Album, yaitu judulnya.
        """
        return self.title

    def get_album_folder_path(self):
        """
        Menghasilkan path folder untuk album berdasarkan judulnya.
        
        Returns:
            str: Path lengkap ke folder album.
        """
        return os.path.join(settings.MEDIA_ROOT, 'albums', slugify(self.title))

    @property
    def slug(self):
        """
        Menghasilkan slug dari judul album.
        """
        return slugify(self.title)


# Signal untuk membuat folder saat album dibuat
@receiver(post_save, sender=Album)
def create_album_folder(sender, instance, created, **kwargs):
    """
    Signal handler yang dipanggil setelah album disimpan.
    Jika album baru dibuat, maka akan dibuat folder fisik untuk album tersebut.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Album): Instance album yang disimpan.
        created (bool): True jika album baru dibuat.
    """
    if created:
        folder_path = instance.get_album_folder_path()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)  # Membuat folder baru


# Signal untuk rename folder saat album diupdate
@receiver(pre_save, sender=Album)
def rename_album_folder(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil sebelum album disimpan.
    Jika judul album berubah, maka folder fisik akan di-rename sesuai judul baru.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Album): Instance album yang akan disimpan.
    """
    if instance.pk:
        try:
            old_instance = Album.objects.get(pk=instance.pk)
            old_folder_path = old_instance.get_album_folder_path()
            new_folder_path = instance.get_album_folder_path()

            # Jika title album berubah, rename folder
            if old_instance.title != instance.title:
                if os.path.exists(old_folder_path):
                    os.rename(old_folder_path, new_folder_path)
        except Album.DoesNotExist:
            # Jika album tidak ditemukan, tidak ada tindakan yang diambil
            pass


# Signal untuk hapus folder saat album dihapus
@receiver(post_delete, sender=Album)
def delete_album_folder(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil setelah album dihapus.
    Menghapus folder fisik beserta isinya terkait dengan album tersebut.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Album): Instance album yang dihapus.
    """
    folder_path = instance.get_album_folder_path()
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Menghapus folder dan isinya
