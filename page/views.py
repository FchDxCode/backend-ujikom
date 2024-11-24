# page/views.py

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from .models import Page
from users.permissions import AllowAny, IsAdmin
from .serializers import PageSerializer
from .utils import create_page_folder, delete_page_folder, rename_page_folder
from django.utils.text import slugify
from gallery.throttles import AdminRateThrottle


class PublicPageView(generics.ListAPIView):
    """
    View untuk menampilkan daftar semua halaman yang bersifat publik.

    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua Page yang aktif.
        serializer_class (Serializer): Serializer yang digunakan adalah PageSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
    """
    queryset = Page.objects.filter(is_active=True)
    serializer_class = PageSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar semua halaman publik.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data halaman.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Pages retrieved successfully",
            "data": serializer.data
        })


class PageViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk operasi CRUD pada model Page.

    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua Page.
        serializer_class (Serializer): Serializer yang digunakan adalah PageSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini hanya dapat diakses oleh pengguna yang terautentikasi (IsAuthenticated).
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    throttle_classes = [AdminRateThrottle]
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        """
        Menghandle permintaan POST untuk membuat Page baru.
        Termasuk pembuatan folder, pembuatan slug, dan penyimpanan Page.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data Page yang dibuat.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "status": "success",
            "status_code": status.HTTP_201_CREATED,
            "message": "Page created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """
        Metode tambahan untuk menangani pembuatan Page.
        Termasuk pembuatan folder halaman berdasarkan slug.

        Args:
            serializer (Serializer): Serializer yang divalidasi dan akan disimpan.

        Returns:
            None
        """
        title = serializer.validated_data['title']
        slug = slugify(title)
        create_page_folder(slug)  # Membuat folder halaman berdasarkan slug
        serializer.save(slug=slug)  # Menyimpan Page dengan slug yang telah dibuat

    def update(self, request, *args, **kwargs):
        """
        Menghandle permintaan PUT/PATCH untuk memperbarui Page tertentu.
        Termasuk penggantian slug dan pengelolaan folder halaman jika terjadi perubahan slug.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data Page yang diperbarui.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_slug = instance.slug
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, old_slug)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Page updated successfully",
            "data": serializer.data
        })

    def perform_update(self, serializer, old_slug):
        """
        Metode tambahan untuk menangani update pada Page.
        Termasuk pengecekan perubahan nama halaman dan mengatur ulang folder serta slug.

        Args:
            serializer (Serializer): Serializer yang divalidasi dan akan disimpan.
            old_slug (str): Slug lama dari Page sebelum diperbarui.

        Returns:
            None
        """
        new_title = serializer.validated_data.get('title', serializer.instance.title)
        new_slug = slugify(new_title)
        if old_slug != new_slug:
            rename_page_folder(old_slug, new_slug)  # Mengganti nama folder jika slug berubah
        serializer.save(slug=new_slug)  # Menyimpan Page dengan slug baru

    def destroy(self, request, *args, **kwargs):
        """
        Menghandle permintaan DELETE untuk menghapus Page tertentu.
        Termasuk penghapusan folder halaman terkait sebelum menghapus instance.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data None.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success",
            "status_code": status.HTTP_204_NO_CONTENT,
            "message": "Page deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        """
        Metode tambahan untuk menghapus Page.
        Termasuk penghapusan folder halaman terkait.

        Args:
            instance (Page): Instance Page yang akan dihapus.

        Returns:
            None
        """
        delete_page_folder(instance.slug)  # Menghapus folder halaman terkait
        instance.delete()  # Menghapus instance Page

    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar semua Page.
        Termasuk pengurutan dan pagination jika diperlukan.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data Page.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Pages retrieved successfully",
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Pages retrieved successfully",
            "data": serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mengambil detail Page tertentu.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data Page.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Page retrieved successfully",
            "data": serializer.data
        })


class PublicPageDetailView(generics.RetrieveAPIView):
    """
    View untuk menampilkan detail halaman publik berdasarkan slug.

    Attributes:
        serializer_class (Serializer): Serializer yang digunakan adalah PageSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
        lookup_field (str): Field yang digunakan untuk mencari objek, yaitu 'slug'.
    """
    serializer_class = PageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Menyesuaikan queryset untuk hanya mengambil Page yang aktif berdasarkan slug.

        Returns:
            QuerySet: Page yang aktif dan sesuai dengan slug yang diberikan.
        """
        return Page.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan detail Page berdasarkan slug.
        Menangani kasus di mana Page tidak ditemukan.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data Page jika ditemukan.
                      Jika tidak ditemukan, respon dengan status error dan kode status 404.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Page retrieved successfully",
                "data": serializer.data
            })
        except Page.DoesNotExist:
            return Response({
                "status": "error",
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Page not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
