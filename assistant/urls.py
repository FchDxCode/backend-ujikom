# assistant/urls.py
from django.urls import path
from .views import GalleryAssistantView  # Ubah nama import sesuai class di views.py

app_name = 'assistant'

urlpatterns = [
    path('public-chat/', GalleryAssistantView.as_view(), name='public-chat'),
]