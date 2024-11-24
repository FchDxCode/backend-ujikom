from django.apps import AppConfig

class AssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assistant'
    
    def ready(self):
        """Initialize AI service when Django starts"""
        from .ai_services import GalleryAssistantService
        # Initialize the service
        GalleryAssistantService()