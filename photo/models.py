# photo/models.py

import os
import shutil
from django.db import models
from album.models import Album
from users.models import User
from django.utils.text import slugify
from django.conf import settings
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from photo.utils import refresh_photo_paths, hash_filename
from django.db.models import Max


# Fungsi untuk mendapatkan path penyimpanan foto berdasarkan album
def get_album_upload_path(instance, filename):
    from photo.utils import hash_filename
    album_title = slugify(instance.album.title)  # Slugify nama album
    # Hash the filename before saving
    hashed_filename = hash_filename(filename)
    # Menyimpan gambar di dalam folder album yang sesuai
    return os.path.join('albums', album_title, hashed_filename)


class Photo(models.Model):
    """
    Model yang merepresentasikan Foto dalam album.
    
    Fields:
        title (CharField): Judul foto.
        description (TextField): Deskripsi foto.
        photo (ImageField): File gambar foto yang diupload.
        album (ForeignKey): Relasi ke model Album.
        uploaded_at (DateTimeField): Tanggal dan waktu foto diupload.
        uploaded_by (ForeignKey): Relasi ke model User yang mengupload foto.
        sequence_number (PositiveIntegerField): Nomor urut foto dalam album.
        likes (PositiveIntegerField): Jumlah likes yang diterima foto.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.ImageField(upload_to=get_album_upload_path)  # Menentukan folder tempat menyimpan foto
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    sequence_number = models.PositiveIntegerField(blank=True, null=True)
    likes = models.PositiveIntegerField(default=0) 
    
    class Meta:
        ordering = ['sequence_number']  # Mengatur urutan berdasarkan sequence_number

    def save(self, *args, **kwargs):
        """
        Override method save untuk mengatur sequence_number sebelum menyimpan.
        
        Jika sequence_number belum diatur, akan diatur ke nilai maksimal sequence_number yang ada + 1.
        """
        if self.sequence_number is None:
            max_sequence = Photo.objects.filter(album=self.album).aggregate(Max('sequence_number'))['sequence_number__max']
            self.sequence_number = (max_sequence or 0) + 1
        super().save(*args, **kwargs)  # Menyimpan instance

    def delete(self, *args, **kwargs):
        """
        Override method delete untuk menangani penghapusan foto.
        
        Termasuk pengaturan ulang cover_photo pada album jika foto yang dihapus adalah cover,
        serta mengatur ulang sequence_number foto lainnya dalam album.
        """
        album = self.album
        sequence_number = self.sequence_number
        
        # Cek apakah foto ini adalah cover album
        is_cover = album.cover_photo == self
        
        super().delete(*args, **kwargs)  # Menghapus instance
        
        # Jika foto yang dihapus adalah cover, set cover baru
        if is_cover:
            # Ambil foto pertama yang tersisa di album
            next_photo = Photo.objects.filter(album=album).first()
            if next_photo:
                album.cover_photo = next_photo
                album.save()
        
        # Sesuaikan urutan foto lain dalam album yang sama
        Photo.objects.filter(
            album=album, 
            sequence_number__gt=sequence_number
        ).update(sequence_number=models.F('sequence_number') - 1)
                          
    def __str__(self):
        """
        Representasi string dari objek Photo, yaitu judul foto.
        
        Returns:
            str: Judul foto.
        """
        return self.title
    
    @staticmethod
    def reset_sequence_numbers(album):
        """
        Metode statis untuk mengatur ulang sequence_number semua foto dalam album.
        
        Args:
            album (Album): Album yang sequence_number fotonya akan diatur ulang.
        
        Returns:
            None
        """
        photos = Photo.objects.filter(album=album).order_by('sequence_number')
        for index, photo in enumerate(photos, start=1):
            if photo.sequence_number != index:
                photo.sequence_number = index
                photo.save()

    @property
    def slug(self):
        """
        Menghasilkan slug dari judul foto.
        """
        return slugify(self.title)


# Signal untuk rename folder foto dan update path foto jika nama album berubah
@receiver(pre_save, sender=Album)
def rename_photo_folder(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil sebelum Album disimpan.
    Mengganti nama folder foto dan memperbarui path foto jika nama album berubah.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Album): Instance Album yang akan disimpan.
        **kwargs: Argumen kata kunci tambahan.
    
    Returns:
        None
    """
    if instance.pk:
        try:
            old_instance = Album.objects.get(pk=instance.pk)
            old_folder = os.path.join(settings.MEDIA_ROOT, 'albums', slugify(old_instance.title))
            new_folder = os.path.join(settings.MEDIA_ROOT, 'albums', slugify(instance.title))

            if old_folder != new_folder and os.path.exists(old_folder):
                os.rename(old_folder, new_folder)  # Rename folder lama ke nama baru
                
                # Update path foto-foto di album ini
                photos = Photo.objects.filter(album=instance)
                for photo in photos:
                    # Buat path baru untuk foto
                    old_photo_path = os.path.join(old_folder, os.path.basename(photo.photo.name))
                    new_photo_path = os.path.join(new_folder, os.path.basename(photo.photo.name))
                    
                    # Jika file foto ada, pindahkan ke folder baru
                    if os.path.exists(old_photo_path):
                        os.rename(old_photo_path, new_photo_path)

                    # Update path di database
                    relative_new_photo_path = os.path.join('albums', slugify(instance.title), os.path.basename(photo.photo.name))
                    photo.photo.name = relative_new_photo_path  # Simpan path baru di database
                    photo.save()

        except Album.DoesNotExist:
            pass


# Signal untuk hapus folder jika album dihapus
@receiver(post_delete, sender=Album)
def delete_album_folder(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil setelah Album dihapus.
    Menghapus folder album beserta seluruh isinya.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Album): Instance Album yang telah dihapus.
        **kwargs: Argumen kata kunci tambahan.
    
    Returns:
        None
    """
    album_folder = os.path.join(settings.MEDIA_ROOT, 'albums', slugify(instance.title))
    if os.path.exists(album_folder):
        shutil.rmtree(album_folder)  # Menghapus folder dan semua file di dalamnya


# Signal untuk memanggil refresh_photo_paths() setelah album diupdate
@receiver(post_save, sender=Album)
def update_photo_paths_on_album_save(sender, instance, **kwargs):
    """
    Signal handler yang dipanggil setelah Album disimpan.
    Memanggil fungsi refresh_photo_paths untuk memperbarui path foto.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Album): Instance Album yang telah disimpan.
        **kwargs: Argumen kata kunci tambahan.
    
    Returns:
        None
    """
    refresh_photo_paths()


# Signal untuk set cover photo jika foto baru diupload
@receiver(post_save, sender=Photo)
def set_album_cover(sender, instance, created, **kwargs):
    """
    Signal handler yang dipanggil setelah Photo disimpan.
    Mengatur cover_photo pada album jika foto yang diupload adalah yang pertama.
    
    Args:
        sender (Model): Model yang mengirim signal.
        instance (Photo): Instance Photo yang telah disimpan.
        created (bool): Indikator apakah Photo baru dibuat.
        **kwargs: Argumen kata kunci tambahan.
    
    Returns:
        None
    """
    if created:
        album = instance.album
        # Jika album belum memiliki cover photo, gunakan foto ini
        if not album.cover_photo:
            album.cover_photo = instance
            album.save()

