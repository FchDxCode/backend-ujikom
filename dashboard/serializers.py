from rest_framework import serializers

class ModelStatsSerializer(serializers.Serializer):
    """
    Serializer untuk statistik dasar model
    """
    total = serializers.IntegerField()
    active = serializers.IntegerField(required=False)
    inactive = serializers.IntegerField(required=False)

class UserStatsSerializer(serializers.Serializer):
    """
    Serializer untuk statistik user
    """
    total = serializers.IntegerField()
    admin = serializers.IntegerField()
    petugas = serializers.IntegerField()

class AnalyticsStatsSerializer(serializers.Serializer):
    """
    Serializer untuk statistik analytics
    """
    total_views = serializers.IntegerField()
    recent_views = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()
    successful_requests = serializers.IntegerField()
    period_days = serializers.IntegerField()

class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer utama untuk dashboard statistics
    """
    users = UserStatsSerializer()
    categories = ModelStatsSerializer()
    albums = ModelStatsSerializer()
    photos = ModelStatsSerializer()
    pages = ModelStatsSerializer()
    content_blocks = ModelStatsSerializer()
    analytics = AnalyticsStatsSerializer()
