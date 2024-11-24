from django.urls import path
from .views import AnalyticsStatsView, AnalyticsArchiveView

app_name = 'analytics'

urlpatterns = [
    path('stats/', AnalyticsStatsView.as_view(), name='stats'),
    path('archives/', AnalyticsArchiveView.as_view(), name='archives'),
    path('archives/<str:filename>/', AnalyticsArchiveView.as_view(), name='download-archive'),
]
