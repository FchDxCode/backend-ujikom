# views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer
from users.permissions import AllowAny, IsPetugas
from gallery.throttles import PetugasRateThrottle

class CategoryPublicListView(generics.ListAPIView):
    """
    View untuk menampilkan daftar semua kategori yang bersifat publik.
    
    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua kategori.
        serializer_class (Serializer): Serializer yang digunakan adalah CategorySerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  

    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar semua kategori publik.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status dan data kategori.
        """
        queryset = self.get_queryset().order_by('sequence_number')
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    View untuk menampilkan daftar semua kategori atau membuat kategori baru.
    
    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua kategori.
        serializer_class (Serializer): Serializer yang digunakan adalah CategorySerializer.
        permission_classes (list): Menentukan bahwa endpoint ini hanya dapat diakses oleh pengguna yang terautentikasi (IsAuthenticated).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [PetugasRateThrottle]
    permission_classes = [IsPetugas] 

    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar semua kategori.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status dan data kategori.
        """
        queryset = self.get_queryset().order_by('sequence_number') 
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    def perform_create(self, serializer):
        """
        Menyimpan kategori baru.
        
        Args:
            serializer (Serializer): Serializer yang divalidasi dan akan disimpan.
        
        Returns:
            None
        """
        serializer.save()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View untuk mengambil, memperbarui, atau menghapus kategori tertentu.
    
    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua kategori.
        serializer_class (Serializer): Serializer yang digunakan adalah CategorySerializer.
        permission_classes (list): Menentukan bahwa endpoint ini hanya dapat diakses oleh pengguna yang terautentikasi (IsAuthenticated).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [PetugasRateThrottle]
    permission_classes = [IsPetugas]

    def retrieve(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mengambil detail kategori tertentu.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status dan data kategori.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "connected",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Menghandle permintaan PUT/PATCH untuk memperbarui kategori tertentu.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status dan data kategori yang diperbarui.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "status": "update",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Menghandle permintaan DELETE untuk menghapus kategori tertentu.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status penghapusan.
        """
        instance = self.get_object()
        instance.delete()
        Category.restructure_sequence_numbers()  # Panggil metode ini setelah kategori dihapus
        return Response({
            "status": "deleted",
            "data": f"Category dengan id {kwargs['pk']} telah dihapus."
        }, status=status.HTTP_204_NO_CONTENT)
