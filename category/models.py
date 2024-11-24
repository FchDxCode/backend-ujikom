# models.py

from django.db import models
from django.db.models import Max
from django.utils.text import slugify


class Category(models.Model):
    """
    Model yang merepresentasikan Kategori dalam sistem.
    
    Fields:
        name (CharField): Nama kategori yang unik.
        description (TextField): Deskripsi kategori, opsional.
        sequence_number (PositiveIntegerField): Nomor urut kategori untuk penataan.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    sequence_number = models.PositiveIntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)  # Menambahkan field created_at

    def save(self, *args, **kwargs):
        """
        Override method save untuk mengatur sequence_number secara otomatis
        saat kategori baru ditambahkan.
        """
        if self._state.adding:  # Jika objek baru ditambahkan
            max_sequence_number = Category.objects.aggregate(max_seq=Max('sequence_number'))['max_seq']
            if max_sequence_number is not None:
                self.sequence_number = max_sequence_number + 1
            else:
                self.sequence_number = 1
        super(Category, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override method delete untuk memastikan sequence_number diubah
        setelah penghapusan kategori.
        """
        super(Category, self).delete(*args, **kwargs)
        self.restructure_sequence_numbers()

    @staticmethod
    def restructure_sequence_numbers():
        """
        Metode statis untuk mengatur ulang sequence_number semua kategori
        setelah terjadi penghapusan, memastikan urutan yang konsisten.
        """
        categories = Category.objects.all().order_by('sequence_number')
        for index, category in enumerate(categories, start=1):
            category.sequence_number = index
            category.save()

    def __str__(self):
        """
        Representasi string dari objek Category, yaitu namanya.
        """
        return self.name

    @property
    def slug(self):
        """
        Menghasilkan slug dari nama kategori.
        """
        return slugify(self.name)

    