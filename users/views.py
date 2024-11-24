# views.py - View untuk mengelola user, autentikasi, registrasi, dan logout

from rest_framework import generics, status
from .models import User
from .serializers import UserSerializer, RegisterUserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdmin, IsAuthenticatedUser
from gallery.throttles import AdminRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging


logger = logging.getLogger(__name__)

class UserListCreateView(generics.ListCreateAPIView):
    """
    View untuk menampilkan daftar user dan membuat user baru.
    Hanya admin yang bisa membuat user baru.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    throttle_classes = [AdminRateThrottle]
    permission_classes = [IsAdmin]  # Semua bisa lihat, hanya admin bisa create
    
    def list(self, request, *args, **kwargs):
        """
        Menampilkan daftar semua user yang terdaftar dalam format respons standar.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View untuk mengambil, memperbarui, atau menghapus user tertentu berdasarkan ID.
    Hanya admin yang bisa mengakses.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]  # Hanya admin yang bisa akses
    throttle_classes = [AdminRateThrottle]
    def update(self, request, *args, **kwargs):
        """
        Memperbarui data user yang ada dengan validasi.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "updated",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View untuk mengelola login dan menghasilkan token JWT dengan role user.
    
    Menambahkan logging untuk memantau upaya login dan hasilnya.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Menangani request login dan menghasilkan respons token dengan logging.
        """
        logger.debug(f"Login attempt with data: {request.data}")
        response = super().post(request, *args, **kwargs)
        logger.debug(f"Login response: {response.data}")
        return response

class RegisterUserView(APIView):
    """
    View untuk registrasi user baru.
    Hanya admin yang bisa mendaftarkan user baru.
    """
    permission_classes = [IsAdmin]  # Hanya admin yang bisa registrasi user baru
    throttle_classes = [AdminRateThrottle]
    def post(self, request):
        """
        Menangani request registrasi user baru.
        
        Hanya dapat diakses oleh user dengan role 'admin'.
        """
        if request.user.role != 'admin':
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Mengambil data user yang terhubung (authenticated).
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "connected",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Memperbarui data user dengan validasi.
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
        Menghapus user yang dipilih.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "deleted",
            "data": f"User dengan id {kwargs['pk']} telah dihapus."
        }, status=status.HTTP_204_NO_CONTENT)

# users/views.py
class LogoutView(APIView):
    """
    View untuk logout user.
    Semua user yang terautentikasi bisa logout.
    """
    permission_classes = [IsAuthenticatedUser]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")  
            if not refresh_token:
                return Response({
                    "status": "error",
                    "message": "Refresh token is required",
                    "code": "token_required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validasi dan blacklist token
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": "Invalid refresh token",
                    "code": "token_invalid"
                }, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"User {request.user.username} logged out successfully")
            
            return Response({
                "status": "success",
                "message": "User logged out successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error for user {request.user.username}: {str(e)}")
            return Response({
                "status": "error",
                "message": str(e),
                "code": "server_error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)