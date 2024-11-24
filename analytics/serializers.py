from rest_framework import serializers
from .models import Analytics

class AnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer untuk model Analytics.
    """
    class Meta:
        model = Analytics
        fields = [
            'path',
            'method',
            'timestamp',
            'ip_address',
            'user_agent',
            'is_authenticated',
            'response_status'
        ]

class AnalyticsStatsSerializer(serializers.Serializer):
    """
    Serializer untuk statistik Analytics.
    """
    total_views = serializers.IntegerField()
    recent_views = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()
    successful_requests = serializers.IntegerField()
    period_days = serializers.IntegerField()

    # Optional: Tambahkan validasi jika diperlukan
    def validate_period_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Period days must be greater than 0")
        return value
