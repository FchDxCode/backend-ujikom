# serializers.py - Serializer untuk model User dan token autentikasi

from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging
from django.contrib.auth.hashers import make_password

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer untuk model User, digunakan untuk serialisasi data user dalam API.
    
    Fields:
    - `id`: ID unik user.
    - `username`: Nama pengguna.
    - `password`: Kata sandi, diatur sebagai `write_only`.
    - `role`: Peran user (misalnya, admin atau petugas).
    
    Metode:
    - `create`: Membuat user baru dengan hashing password.
    - `update`: Mengubah data user, termasuk hashing password jika ada perubahan.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': False}
        }

    def create(self, validated_data):
        """
        Membuat user baru dengan hashing password.
        
        Parameter:
        - `validated_data`: Data yang telah divalidasi untuk user.

        Mengembalikan:
        - Objek user yang baru dibuat.
        """
        user = User(
            username=validated_data['username'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])  # Hashing password
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """
        Mengubah data user, termasuk hashing password jika ada perubahan password.
        
        Parameter:
        - `instance`: Instance user yang akan diupdate.
        - `validated_data`: Data yang telah divalidasi.

        Mengembalikan:
        - Instance user yang telah diupdate.
        """
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()  # Simpan instance setelah mengubah password
            validated_data.pop('password')

        return super().update(instance, validated_data)
    
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer kustom untuk menghasilkan token JWT dengan informasi tambahan.
    
    Menambahkan field `role` ke dalam token payload untuk mencantumkan peran user.
    
    Metode:
    - `get_token`: Menambahkan role user ke token.
    - `validate`: Memvalidasi data user dan menambahkan role ke respons.
    """
    @classmethod
    def get_token(cls, user):
        """
        Menghasilkan token JWT dengan informasi role user.
        
        Parameter:
        - `user`: User yang tokennya akan dibuat.

        Mengembalikan:
        - Token JWT dengan informasi tambahan `role`.
        """
        token = super().get_token(user)

        token['role'] = user.role  # Tambahkan peran user ke payload token
        logger.debug(f"Token created for user {user.username} with role {user.role}")
        return token

    def validate(self, attrs):
        """
        Memvalidasi data user dan menambahkan informasi role ke respons.

        Parameter:
        - `attrs`: Atribut validasi dari user.

        Mengembalikan:
        - Data respons yang mencakup role user.
        """
        data = super().validate(attrs)
        logger.debug(f"Validating user with attributes: {attrs}")

        data['role'] = self.user.role  # Tambahkan role user ke respons
        logger.debug(f"Validation successful, data: {data}")
        return data


class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Serializer untuk registrasi user baru, mirip dengan UserSerializer tetapi menambahkan
    fitur pendaftaran dan pengaktifan user.

    Fields:
    - `id`: ID unik user.
    - `username`: Nama pengguna.
    - `password`: Kata sandi, diatur sebagai `write_only`.
    - `role`: Peran user (misalnya, admin atau petugas).
    
    Metode:
    - `create`: Membuat user baru dengan hashing password dan mengaktifkan status.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': False}
        }

    def create(self, validated_data):
        """
        Membuat user baru dengan hashing password dan mengaktifkan status user.

        Parameter:
        - `validated_data`: Data yang telah divalidasi untuk user.

        Mengembalikan:
        - Objek user yang baru dibuat.
        """
        user = User(
            username=validated_data['username'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])  # Hashing password
        user.is_active = True  # Aktifkan user secara default
        user.save()
        return user
