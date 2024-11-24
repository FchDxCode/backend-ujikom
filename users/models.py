from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    """
    Manager khusus untuk model User yang menyediakan metode pembuatan user reguler dan superuser.
    
    Metode:
    - `create_user`: Membuat user baru dengan `username`, `password`, dan `role` (default: 'petugas').
    - `create_superuser`: Membuat superuser dengan `username` dan `password`, dan menambahkan atribut
      tambahan `is_staff` dan `is_superuser` untuk otorisasi admin.
    """
    def create_user(self, username, password=None, role='petugas', **extra_fields):
        """
        Membuat dan menyimpan user baru dengan username dan password.

        Parameter:
        - `username`: Username yang wajib diisi untuk setiap user.
        - `password`: Password yang akan di-hash sebelum disimpan.
        - `role`: Peran atau role user dalam aplikasi (default: 'petugas').

        Mengembalikan:
        - Objek user yang baru dibuat.
        
        Munculkan Error:
        - `ValueError` jika username tidak disediakan.
        """
        if not username:
            raise ValueError('Users must have a username')
        
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.is_active = True  # Default user diaktifkan
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Membuat dan menyimpan superuser dengan `username` dan `password`.
        
        Parameter:
        - `username`: Username untuk superuser.
        - `password`: Password untuk superuser.

        Mengembalikan:
        - Objek superuser yang baru dibuat.

        Munculkan Error:
        - `ValueError` jika `is_staff` atau `is_superuser` tidak `True`.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, role='admin', **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Model kustom untuk User yang mendukung sistem autentikasi berbasis username.
    
    Atribut:
    - `username`: Nama unik yang digunakan untuk login.
    - `password`: Kata sandi user yang disimpan dalam format hash.
    - `role`: Peran user dalam aplikasi, baik 'admin' atau 'petugas'.
    - `is_active`: Status aktif user, default `True`.
    - `is_staff`: Menunjukkan apakah user memiliki akses ke situs admin, default `False`.
    - `is_superuser`: Menunjukkan apakah user adalah superuser, default `False`.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('petugas', 'Petugas'),
    )

    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False) 

    objects = UserManager()

    USERNAME_FIELD = 'username'  # Field yang digunakan sebagai identifikasi user

    def __str__(self):
        """
        Mengembalikan representasi string dari user sebagai username.
        """
        return self.username
