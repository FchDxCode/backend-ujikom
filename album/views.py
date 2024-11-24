# album/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Album
from .serializers import AlbumSerializer
from gallery.throttles import PetugasRateThrottle
from users.permissions import AllowAny, IsPetugas


class PublicAlbumListView(generics.ListAPIView):
    """
    View untuk menampilkan daftar semua album yang aktif dan bersifat publik.
    
    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua album yang aktif dan diurutkan berdasarkan sequence_number.
        serializer_class (Serializer): Serializer yang digunakan adalah AlbumSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
    """
    queryset = Album.objects.filter(is_active=True).order_by('sequence_number')
    serializer_class = AlbumSerializer
    permission_classes = [AllowAny]  

    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar album publik.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status dan data album.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AlbumListCreateView(generics.ListCreateAPIView):
    """
    View untuk menampilkan daftar semua album atau membuat album baru.
    
    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua album yang diurutkan berdasarkan sequence_number.
        serializer_class (Serializer): Serializer yang digunakan adalah AlbumSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini hanya dapat diakses oleh pengguna yang terautentikasi (IsAuthenticated).
    """
    queryset = Album.objects.all().order_by('sequence_number')  
    serializer_class = AlbumSerializer
    throttle_classes = [PetugasRateThrottle]
    permission_classes = [IsPetugas] 

    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar semua album.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status dan data album.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """
        Menyimpan album baru dengan menetapkan pengguna yang membuatnya.
        
        Args:
            serializer (Serializer): Serializer yang divalidasi dan akan disimpan.
        
        Returns:
            Response: Respon JSON dengan status dan data album yang dibuat.
        """
        album = serializer.save(created_by=self.request.user)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class AlbumDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View untuk mengambil, memperbarui, atau menghapus album tertentu.
    
    Attributes:
        queryset (QuerySet): Kueri untuk mengambil semua album.
        serializer_class (Serializer): Serializer yang digunakan adalah AlbumSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini hanya dapat diakses oleh pengguna yang terautentikasi (IsAuthenticated).
    """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    throttle_classes = [PetugasRateThrottle]
    permission_classes = [IsPetugas]

    def retrieve(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mengambil detail album tertentu.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status dan data album.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "connected",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Menghandle permintaan PUT/PATCH untuk memperbarui album tertentu.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status dan data album yang diperbarui.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "status": "updated",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Menghandle permintaan DELETE untuk menghapus album tertentu.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status penghapusan.
        """
        instance = self.get_object()
        instance.delete()
        Album.restructure_sequence_numbers()  
        return Response({
            "status": "deleted",
            "data": f"Album dengan id {kwargs['pk']} telah dihapus."
        }, status=status.HTTP_204_NO_CONTENT)


class AlbumByCategoryView(generics.ListAPIView): 
    """
    View untuk menampilkan daftar album berdasarkan kategori tertentu.
    
    Attributes:
        queryset (QuerySet): Kueri default untuk mengambil semua album yang aktif.
        serializer_class (Serializer): Serializer yang digunakan adalah AlbumSerializer.
        permission_classes (list): Menentukan bahwa endpoint ini dapat diakses oleh siapa saja (AllowAny).
    """
    queryset = Album.objects.filter(is_active=True)
    serializer_class = AlbumSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Menyesuaikan queryset berdasarkan category_id yang diberikan dalam URL.
        
        Returns:
            QuerySet: Album yang termasuk dalam kategori tertentu.
        """
        category_id = self.kwargs['category_id']
        return Album.objects.filter(category__id=category_id)
    
    def list(self, request, *args, **kwargs):
        """
        Menghandle permintaan GET untuk mendapatkan daftar album berdasarkan kategori.
        
        Args:
            request (HttpRequest): Objek permintaan HTTP.
            *args: Argumen posisi tambahan.
            **kwargs: Argumen kata kunci tambahan.
        
        Returns:
            Response: Respon JSON dengan status, kode status, dan data album.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data,
        }
        
        return Response(response_data)
