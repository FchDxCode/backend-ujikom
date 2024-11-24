# assistant/ai_services.py
from .ai_core import GalleryAICore
from .models import AssistantContext, ChatHistory, InteractionLog
from googletrans import Translator
import numpy as np
from .responses import GalleryResponses
from datetime import datetime
from album.models import Album
from photo.models import Photo
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify
from .dynamic_data_services import DynamicDataService
import random

class GalleryAssistantService:
    """Service layer untuk Gallery Assistant"""
    
    _instance = None
    _ai_core = None
    
    def __new__(cls):
        if cls._instance is None:
            print("Creating new GalleryAssistantService instance")
            cls._instance = super().__new__(cls)
            cls._instance._ai_core = GalleryAICore()
        return cls._instance

    def __init__(self):
        # Skip initialization if already initialized
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.translator = Translator()
        print("GalleryAssistantService initialized")

    @property
    def ai_core(self):
        return self._ai_core

    def process_query(self, query, session_id):
        """Process user query and generate response"""
        try:
            print(f"Processing query: {query}")
            
            # Validate query
            if not query or not self.ai_core.is_safe_query(query):
                print("Query invalid or unsafe")
                return {'text': GalleryResponses.get_error_response('id')}

            # Analyze with context
            analysis = self.ai_core.analyze_text(query)
            print(f"Analysis result: {analysis}")
            
            language = analysis['language']
            intent = analysis['intent']
            
            # Handle popular photos intent
            if intent == 'popular_photos':
                dynamic_data = self._get_dynamic_data(intent, language)
                if dynamic_data:
                    response = {
                        'text': {
                            'intro': GalleryResponses.DYNAMIC_RESPONSES['popular_photos'][language],
                            'text': dynamic_data,
                            'outro': "Ada yang ingin ditanyakan lagi? 😊"
                        },
                        'isDynamic': True
                    }
                    print(f"Dynamic response: {response}")  # Debug log
                    return response
            
            # Handle greeting intent
            if intent == 'greeting':
                greeting_response = random.choice(GalleryResponses.GENERAL_RESPONSES['greeting'][language])
                response = {'text': greeting_response}
                print(f"Greeting response: {response}")  # Debug log
                return response
            
            # Handle about intent
            if intent == 'about':
                about_response = GalleryResponses.RESPONSES['about'][language]['text']
                response = {'text': about_response}
                print(f"About response: {response}")  # Debug log
                return response
            
            # Handle casual intent
            if intent == 'casual':
                casual_responses = GalleryResponses.RESPONSES['casual'][language]['text']
                casual_response = random.choice(casual_responses)
                response = {'text': casual_response}
                print(f"Casual response: {response}")  # Debug log
                return response

            # Default response if no specific intent is matched
            default_response = {'text': GalleryResponses.GENERAL_RESPONSES['not_understood'][language]}
            print(f"Default response: {default_response}")  # Debug log
            return default_response

        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return {'text': GalleryResponses.get_error_response(language)}

    def _generate_response(self, query, analysis, context):
        """Generate contextual response"""
        language = analysis['language']
        intent = analysis['intent']
        
        # Cek apakah intent memerlukan data dinamis
        if intent in ['popular_photos', 'latest_photos', 'latest_albums', 'latest_informasi', 'latest_agenda']:
            dynamic_data = self._get_dynamic_data(intent, language)
            if dynamic_data:
                template = GalleryResponses.DYNAMIC_RESPONSES[intent][language]
                return {
                    'text': dynamic_data,  # Langsung kirim data array dengan URL
                    'type': 'dynamic_content'
                }

        # Jika bukan intent dinamis, gunakan respons normal
        response_text, similarity = self.ai_core.get_best_response(
            query, language, intent
        )
        return {'text': response_text}

    def _get_sentiment_prefix(self, sentiment, language):
        """Get prefix based on sentiment"""
        if language == 'id':
            if sentiment['label'] in ['5 stars', '4 stars']:
                return "Senang bisa membantu! "
            elif sentiment['label'] in ['1 star', '2 stars']:
                return "Mohon maaf atas kebingungannya. "
        else:
            if sentiment['label'] in ['5 stars', '4 stars']:
                return "Happy to help! "
            elif sentiment['label'] in ['1 star', '2 stars']:
                return "I apologize for any confusion. "
        return ""

    def _get_context(self, session_id):
        """Get conversation context"""
        context, created = AssistantContext.objects.get_or_create(
            session_id=session_id
        )
        return context.context

    def _update_context(self, session_id, query, response, context):
        """Update conversation context with history"""
        try:
            context_obj = AssistantContext.objects.get(session_id=session_id)
            
            # Get existing history or initialize
            history = context.get('conversation_history', [])
            
            # Add new interaction to history
            history.append({
                'query': query,
                'response': response['text'],
                'intent': response.get('intent'),
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 5 interactions for context
            history = history[-5:]
            
            # Update context
            new_context = {
                'last_query': query,
                'last_intent': response.get('intent'),
                'last_topic': self._extract_topic(query),
                'interaction_count': context.get('interaction_count', 0) + 1,
                'has_introduced': context.get('has_introduced', False),
                'conversation_history': history
            }
            
            # Update database
            context_obj.context = new_context
            context_obj.conversation_history = history
            context_obj.conversation_turns += 1
            context_obj.last_intent = response.get('intent')
            context_obj.last_topic = self._extract_topic(query)
            context_obj.save()
            
        except AssistantContext.DoesNotExist:
            # Create new context if doesn't exist
            AssistantContext.objects.create(
                session_id=session_id,
                context={
                    'last_query': query,
                    'interaction_count': 1,
                    'has_introduced': False,
                    'conversation_history': [{
                        'query': query,
                        'response': response['text'],
                        'intent': response.get('intent'),
                        'timestamp': datetime.now().isoformat()
                    }]
                },
                conversation_history=[{
                    'query': query,
                    'response': response['text'],
                    'intent': response.get('intent'),
                    'timestamp': datetime.now().isoformat()
                }],
                conversation_turns=1,
                last_intent=response.get('intent'),
                last_topic=self._extract_topic(query)
            )

    def _log_interaction(self, session_id, query, response, analysis):
        """Log interaction for analytics"""
        try:
            InteractionLog.objects.create(
                session_id=session_id,
                question=query,
                answer=response['text'],
                language=analysis['language'],
                sentiment=analysis['sentiment']['label'],
                intent=analysis['intent'],
                confidence_score=analysis.get('confidence', 0.0),
                is_helpful=self._estimate_helpfulness(response)
            )
        except Exception as e:
            print(f"Error logging interaction: {str(e)}")

    def _estimate_helpfulness(self, response):
        """Estimate if response was helpful based on confidence and clarity"""
        confidence = response.get('confidence', 0)
        requires_clarification = response.get('requires_clarification', False)
        return confidence > 0.7 and not requires_clarification

    def _extract_topic(self, query):
        """Extract main topic from query"""
        # Simple topic extraction based on keywords
        topics = {
            'photo': ['foto', 'gambar', 'picture', 'image'],
            'search': ['cari', 'search', 'find'],
            'help': ['bantuan', 'help', 'guide'],
            'category': ['kategori', 'category', 'album']
        }
        
        query_lower = query.lower()
        for topic, keywords in topics.items():
            if any(keyword in query_lower for keyword in keywords):
                return topic
        return 'general'

    def _get_error_response(self):
        """Get error response"""
        return {
            'text': {
                'id': "Maaf, saya tidak bisa memproses pertanyaan tersebut.",
                'en': "Sorry, I cannot process that question."
            },
            'error': True
        }

    def get_chat_history(self, session_id, limit=10):
        """Get chat history for session"""
        return ChatHistory.objects.filter(
            session_id=session_id
        ).order_by('-created_at')[:limit]

    def _convert_to_native_types(self, obj):
        """Convert numpy/tensor types to Python native types"""
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_to_native_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_native_types(item) for item in obj]
        return obj

    def get_introduction(self, language='id'):
        """Get Cerbi's introduction"""
        return GalleryResponses.get_introduction(language)

    def _get_dynamic_data(self, intent, language='id'):
        """Get dynamic data based on intent"""
        try:
            if intent == 'popular_photos':
                return DynamicDataService.get_popular_photos(language)
            # elif intent == 'latest_informasi':
            #     return DynamicDataService.get_latest_informasi(language)
            # elif intent == 'latest_agenda':
            #     return DynamicDataService.get_latest_agenda(language)
            # elif intent == 'latest_albums':
            #     return DynamicDataService.get_latest_albums(language)
            return None
        except Exception as e:
            print(f"Error getting dynamic data: {str(e)}")
            return None