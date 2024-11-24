from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Permission untuk mengecek apakah user adalah admin.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )

class IsPetugas(BasePermission):
    """
    Permission untuk mengecek apakah user adalah petugas.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'petugas'
        )

class IsAdminOrReadOnly(BasePermission):
    """
    Permission untuk mengizinkan admin melakukan semua operasi,
    tapi user lain hanya bisa membaca.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )

class AllowAny(BasePermission):
    """
    Permission untuk mengizinkan akses publik tanpa autentikasi.
    """
    def has_permission(self, request, view):
        return True
    
    
class IsAuthenticatedUser(BasePermission):
    """
    Permission untuk memastikan user sudah login.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)