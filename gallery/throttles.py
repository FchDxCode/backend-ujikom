from rest_framework.throttling import UserRateThrottle

class PetugasRateThrottle(UserRateThrottle):
    """
    Throttle untuk petugas dengan rate limit 1000/day.
    Membatasi jumlah request yang dapat dilakukan oleh petugas.
    """
    scope = 'petugas'

    def get_cache_key(self, request, view):
        if request.user.role == 'petugas':
            return self.cache_format % {
                'scope': self.scope,
                'ident': request.user.pk
            }
        return None

class AdminRateThrottle(UserRateThrottle):
    """
    Throttle untuk admin dengan rate limit 5000/day.
    Membatasi jumlah request yang dapat dilakukan oleh admin.
    """
    scope = 'admin'

    def get_cache_key(self, request, view):
        if request.user.role == 'admin':
            return self.cache_format % {
                'scope': self.scope,
                'ident': request.user.pk
            }
        return None
