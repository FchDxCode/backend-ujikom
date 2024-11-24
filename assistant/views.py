# assistant/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from .ai_services import GalleryAssistantService
import uuid
from django.db.models import Count
from .models import InteractionLog

class GalleryAssistantView(APIView):
    """View untuk Gallery Assistant"""
    
    permission_classes = [AllowAny]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assistant = GalleryAssistantService()
    
    def post(self, request):
        """Handle chat request"""
        try:
            # Validate input
            question = request.data.get('question', '').strip()
            if not question:
                return Response({
                    'error': 'Question is required'
                }, status=400)
            
            # Get or create session
            session_id = request.session.get('chat_session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                request.session['chat_session_id'] = session_id
            
            # Process query
            response = self.assistant.process_query(question, session_id)
            
            if response.get('error'):
                return Response(response, status=400)
                
            return Response(response)
            
        except Exception as e:
            return Response({
                'error': 'Internal server error'
            }, status=500)
    
    def get(self, request):
        """Get chat history"""
        try:
            session_id = request.session.get('chat_session_id')
            if not session_id:
                return Response([])
            
            history = self.assistant.get_chat_history(session_id)
            data = [{
                'question': chat.question,
                'answer': chat.answer,
                'language': chat.language,
                'sentiment': chat.sentiment,
                'created_at': chat.created_at
            } for chat in history]
            
            return Response(data)
            
        except Exception as e:
            return Response({
                'error': 'Internal server error'
            }, status=500)
    
    def get_analytics(self, request):
        """Get interaction analytics"""
        try:
            # Get basic stats
            total_interactions = InteractionLog.objects.count()
            helpful_interactions = InteractionLog.objects.filter(is_helpful=True).count()
            
            # Get most common intents
            common_intents = InteractionLog.objects.values('intent')\
                .annotate(count=Count('intent'))\
                .order_by('-count')[:5]
            
            # Get language distribution
            language_dist = InteractionLog.objects.values('language')\
                .annotate(count=Count('language'))\
                .order_by('-count')
            
            return Response({
                'total_interactions': total_interactions,
                'helpful_ratio': helpful_interactions / total_interactions if total_interactions > 0 else 0,
                'common_intents': common_intents,
                'language_distribution': language_dist
            })
            
        except Exception as e:
            return Response({
                'error': 'Error fetching analytics'
            }, status=500)