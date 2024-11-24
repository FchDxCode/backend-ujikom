# views.py - View untuk mengelola operasi terkait foto
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Photo, Album
from .serializers import PhotoSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Max
import os
import logging
import json
from users.permissions import AllowAny, IsPetugas
from gallery.throttles import PetugasRateThrottle


logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def like_photo(request, photo_id):
    """
    Fungsi untuk toggle "like" pada foto dengan ID tertentu.
    
    Jika foto belum dilike, tambahkan like dan set cookie.
    Jika foto sudah dilike, kurangi like dan hapus cookie.
    Menggunakan transaksi atomik untuk mencegah inkonsistensi data.
    
    Parameter:
    - `request`: Objek HTTP request.
    - `photo_id`: ID foto yang akan di-toggle like-nya.
    
    Mengembalikan:
    - `JsonResponse`: Status dan jumlah "like" terkini.
    """
    try:
        with transaction.atomic():
            photo = Photo.objects.select_for_update().get(id=photo_id)
            
            # Parse the request body to get the action
            body = json.loads(request.body.decode('utf-8'))
            action = body.get('action')

            if action == 'like':
                photo.likes += 1
                photo.save()
                response_action = 'liked'
            elif action == 'unlike':
                photo.likes = max(0, photo.likes - 1)
                photo.save()
                response_action = 'unliked'
            else:
                return JsonResponse({'status': 'failed', 'message': 'Invalid action.'}, status=400)
            
            return JsonResponse({
                'status': 'success',
                'likes': photo.likes,
                'action': response_action
            })

    except Photo.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'Photo not found.'}, status=404)

class PhotoListPublic(generics.ListCreateAPIView): 
    """
    API untuk menampilkan daftar foto yang dapat diakses publik dan membuat foto baru.
    
    Menggunakan permission "AllowAny" sehingga bisa diakses tanpa autentikasi.
    """
    queryset = Photo.objects.all().order_by('sequence_number')
    serializer_class = PhotoSerializer
    permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        """
        Menampilkan daftar foto dalam format respons standar.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """
        Override metode `perform_create` untuk menyimpan data user yang mengunggah.
        """
        serializer.save(uploaded_by=self.request.user)

class PhotoListCreateView(generics.ListCreateAPIView):
    """
    API untuk membuat dan menampilkan daftar semua foto dengan otorisasi pengguna.
    """
    parser_classes = [MultiPartParser, FormParser]  
    queryset = Photo.objects.all().order_by('sequence_number')
    serializer_class = PhotoSerializer
    permission_classes = [IsPetugas]
    throttle_classes = [PetugasRateThrottle]

    def post(self, request, *args, **kwargs):
        """
        Menangani pengunggahan beberapa foto dan membuat entri untuk setiap foto dalam database.
        Setiap foto akan diberi nomor urut (sequence_number) berdasarkan urutan dalam album.
        """
        files = request.FILES.getlist('photos')
        album_id = request.data.get('album')
        album = Album.objects.get(pk=album_id)
    
        # Mendapatkan nomor urut maksimal untuk penentuan sequence berikutnya
        max_sequence = Photo.objects.filter(album=album).aggregate(Max('sequence_number'))['sequence_number__max'] or 0

        photos_data = []
        for i, file in enumerate(files, start=1):
            title = request.data.get('title', f"Photo {max_sequence + i}")
            description = request.data.get('description', "No description provided")

            logger.debug(f"Title: {title}, Description: {description}")

            photo_data = {
                'title': title,
                'description': description,
                'album': album.id,
                'photo': file,
                'uploaded_by': request.user.id,
                'sequence_number': max_sequence + i
            }
            photos_data.append(photo_data)

        serializer = self.get_serializer(data=photos_data, many=True)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        Menampilkan daftar foto dengan format respons standar.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """
        Menyimpan foto yang diunggah serta album terkait.
        """
        album_id = self.request.data.get('album')
        try:
            album = Album.objects.get(pk=album_id)
        except Album.DoesNotExist:
            raise serializer.ValidationError({"album": "Invalid album ID."})
        
        serializer.save(uploaded_by=self.request.user, album=album)

class PhotoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API untuk mengambil, memperbarui, atau menghapus foto tertentu.
    
    Memerlukan autentikasi pengguna.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsPetugas]
    throttle_classes = [PetugasRateThrottle]

    def update(self, request, *args, **kwargs):
        """
        Mengupdate foto, menghapus gambar lama jika ada gambar baru diunggah.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Menghapus gambar lama jika diganti dengan yang baru
        if 'photo' in request.FILES:
            if instance.photo and os.path.exists(instance.photo.path):
                os.remove(instance.photo.path)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "updated",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Menghapus foto dari database dan file sistem, serta mereset nomor urut (sequence number) dalam album.
        """
        instance = self.get_object()
        album = instance.album
        if instance.photo and os.path.exists(instance.photo.path):
            os.remove(instance.photo.path)
        self.perform_destroy(instance)
        Photo.reset_sequence_numbers(album)  # Reset nomor urut setelah penghapusan
        return Response({
            "status": "deleted",
            "data": f"Photo dengan id {kwargs['pk']} telah dihapus."
        }, status=status.HTTP_204_NO_CONTENT)

class PhotoByAlbumView(generics.ListAPIView):
    """
    API untuk menampilkan foto dalam album tertentu.
    
    Memungkinkan akses tanpa autentikasi.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Mendapatkan queryset untuk foto berdasarkan ID album dari URL.
        """
        album_id = self.kwargs['album_id']
        return Photo.objects.filter(album__id=album_id)

    def list(self, request, *args, **kwargs):
        """
        Menampilkan foto dalam album dalam format respons yang diinginkan.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Membungkus data dalam format respons standar
        response_data = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data,
        }
        
        return Response(response_data)

class PublicPhotoDetailView(generics.RetrieveAPIView):
    """
    API untuk mengambil detail foto untuk publik.
    Hanya bisa digunakan untuk GET request.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        """
        Mengambil detail foto berdasarkan ID untuk publik.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        except Photo.DoesNotExist:
            return Response({
                "status": "error",
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Foto tidak ditemukan"
            }, status=status.HTTP_404_NOT_FOUND)