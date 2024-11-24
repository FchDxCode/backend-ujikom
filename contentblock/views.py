# views.py

from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from .models import ContentBlock
from .serializers import ContentBlockSerializer
from django.utils.text import slugify
from users.permissions import AllowAny, IsAdmin
from page.models import Page
from .utils import (
    create_contentblock_folders, 
    rename_contentblock_folders, 
    refresh_contentblock_paths, 
    delete_contentblock_files, 
    generate_random_filename
)
import os
import logging
from gallery.throttles import AdminRateThrottle
# Mendapatkan instance logger untuk modul ini
logger = logging.getLogger(__name__)


class PublicContentBlockListView(generics.ListAPIView):
    """
    View untuk menampilkan daftar semua ContentBlock yang bersifat publik.

    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua ContentBlock.
        serializer_class (Serializer): Serializer yang digunakan adalah ContentBlockSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
    """
    queryset = ContentBlock.objects.all()
    serializer_class = ContentBlockSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar semua ContentBlock publik.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data ContentBlock.
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Content blocks retrieved successfully",
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Content blocks retrieved successfully",
            "data": serializer.data
        })


class ContentBlockViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk operasi CRUD pada model ContentBlock.

    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua ContentBlock.
        serializer_class (Serializer): Serializer yang digunakan adalah ContentBlockSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini hanya dapat diakses oleh pengguna yang terautentikasi (IsAuthenticated).
    """
    queryset = ContentBlock.objects.all()
    serializer_class = ContentBlockSerializer
    permission_classes =[IsAdmin]
    throttle_classes = [AdminRateThrottle]

    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar semua ContentBlock.
        Juga memperbarui path untuk setiap ContentBlock berdasarkan slug dari page terkait.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data ContentBlock.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Refresh paths untuk semua ContentBlock
        for contentblock in queryset:
            refresh_contentblock_paths(contentblock, slugify(contentblock.page.title))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Content blocks retrieved successfully",
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Content blocks retrieved successfully",
            "data": serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mengambil detail ContentBlock tertentu.
        Juga memperbarui path untuk ContentBlock yang diambil.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data ContentBlock.
        """
        instance = self.get_object()
        
        # Refresh path untuk ContentBlock yang diambil
        refresh_contentblock_paths(instance, slugify(instance.page.title))
        
        serializer = self.get_serializer(instance)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Content block retrieved successfully",
            "data": serializer.data
        })

    def create(self, request, *args, **kwargs):
        """
        Menghandle permintaan POST untuk membuat ContentBlock baru.
        Termasuk pembuatan folder, hashing nama file gambar, dan memperbarui path gambar.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data ContentBlock yang dibuat.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Hash nama file gambar jika ada gambar yang diupload
        if 'image' in request.data and request.data['image']:
            original_file = request.data['image']
            file_extension = os.path.splitext(original_file.name)[1]
            original_file.name = generate_random_filename(file_extension)
        
        # Membuat folder terlebih dahulu
        page_slug = slugify(Page.objects.get(id=request.data['page']).title)
        create_contentblock_folders(page_slug)
        
        # Menyimpan ContentBlock
        contentblock = serializer.save(created_by=self.request.user)
        
        # Memperbarui path jika ada gambar
        if contentblock.image:
            refresh_contentblock_paths(contentblock, page_slug)
        
        return Response({
            "status": "success",
            "status_code": status.HTTP_201_CREATED,
            "message": "Content block created successfully",
            "data": serializer.data
        })

    def update(self, request, *args, **kwargs):
        """
        Menghandle permintaan PUT/PATCH untuk memperbarui ContentBlock tertentu.
        Termasuk penghapusan gambar lama, hashing nama file gambar baru, dan memperbarui path gambar.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data ContentBlock yang diperbarui.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_image_path = instance.image.path if instance.image else None
        
        # Hash nama file gambar jika ada gambar baru yang diupload
        if 'image' in request.data and request.data['image']:
            original_file = request.data['image']
            file_extension = os.path.splitext(original_file.name)[1]
            original_file.name = generate_random_filename(file_extension)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Menghapus gambar lama jika ada dan diganti dengan gambar baru
        if 'image' in request.data:
            if old_image_path and os.path.isfile(old_image_path):
                os.remove(old_image_path)
        
        contentblock = serializer.save()
        
        # Memperbarui path gambar
        refresh_contentblock_paths(contentblock, slugify(contentblock.page.title))
        
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Content block updated successfully",
            "data": serializer.data
        })

    def perform_update(self, serializer):
        """
        Metode tambahan untuk menangani update pada ContentBlock.
        Termasuk pengecekan perubahan nama halaman dan mengatur ulang folder serta path gambar.

        Args:
            serializer (Serializer): Serializer yang divalidasi dan akan disimpan.

        Returns:
            None
        """
        old_page_title = slugify(serializer.instance.page.title)
        contentblock = serializer.save()
        new_page = contentblock.page
        new_slug = slugify(new_page.title)

        # Jika nama halaman berubah, update folder dan path konten
        if old_page_title != new_slug:
            rename_contentblock_folders(old_page_title, new_slug)
            refresh_contentblock_paths(contentblock, new_slug)

        contentblock.set_upload_paths()
        contentblock.save()

    def destroy(self, request, *args, **kwargs):
        """
        Menghandle permintaan DELETE untuk menghapus ContentBlock tertentu.
        Termasuk penghapusan file gambar terkait sebelum menghapus instance.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data None.
        """
        instance = self.get_object()
        
        # Menghapus file sebelum menghapus instance
        delete_contentblock_files(instance)
        self.perform_destroy(instance)
        
        return Response({
            "status": "success",
            "status_code": status.HTTP_204_NO_CONTENT,
            "message": "Content block deleted successfully",
            "data": None
        })

    def perform_destroy(self, instance):
        """
        Metode tambahan untuk menghapus ContentBlock.
        Termasuk penghapusan file gambar terkait.

        Args:
            instance (ContentBlock): Instance ContentBlock yang akan dihapus.

        Returns:
            None
        """
        delete_contentblock_files(instance)
        instance.delete()  # Ini akan memicu signal post_delete untuk mengatur ulang sequence_number


class ContentBlockByPages(generics.ListAPIView):
    """
    View untuk menampilkan daftar ContentBlock berdasarkan ID halaman tertentu.

    Attributes:
        queryset (QuerySet): Kueri default untuk mengambil semua ContentBlock.
        serializer_class (Serializer): Serializer yang digunakan adalah ContentBlockSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
    """
    queryset = ContentBlock.objects.all()
    serializer_class = ContentBlockSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Menyesuaikan queryset berdasarkan page_id yang diberikan dalam URL.

        Returns:
            QuerySet: ContentBlock yang termasuk dalam halaman tertentu.
        """
        page_id = self.kwargs['page_id']
        return ContentBlock.objects.filter(page__id=page_id)
    
    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar ContentBlock berdasarkan halaman.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, dan data ContentBlock.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        }
        
        return Response(response_data)


class ContentBlockByPageSlug(generics.ListAPIView):
    """
    View untuk menampilkan daftar ContentBlock berdasarkan slug halaman tertentu.

    Attributes:
        serializer_class (Serializer): Serializer yang digunakan adalah ContentBlockSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
    """
    serializer_class = ContentBlockSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Menyesuaikan queryset berdasarkan page_slug yang diberikan dalam URL.

        Returns:
            QuerySet: ContentBlock yang termasuk dalam halaman tertentu berdasarkan slug.
        """
        page_slug = self.kwargs['page_slug']
        return ContentBlock.objects.filter(page__slug=page_slug)
    
    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar ContentBlock berdasarkan slug halaman.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data ContentBlock.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Content blocks retrieved successfully",
            "data": serializer.data
        }
        
        return Response(response_data)


class ContentBlockDetailView(generics.RetrieveAPIView):
    """
    View untuk menampilkan detail ContentBlock berdasarkan ID.

    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua ContentBlock.
        serializer_class (Serializer): Serializer yang digunakan adalah ContentBlockSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
    """
    queryset = ContentBlock.objects.all()
    serializer_class = ContentBlockSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan detail ContentBlock berdasarkan ID.

        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.

        Returns:
            Response: Respon JSON dengan status, kode status, pesan, dan data ContentBlock.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Content block retrieved successfully",
                "data": serializer.data
            })
        except ContentBlock.DoesNotExist:
            return Response({
                "status": "error",
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Content block not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
