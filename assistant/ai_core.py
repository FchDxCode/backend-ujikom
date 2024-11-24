# assistant/ai_core.py
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from sentence_transformers import SentenceTransformer
from langdetect import detect
import torch
import numpy as np
from textblob import TextBlob
import os
from pathlib import Path
from .responses import GalleryResponses

class GalleryAICore:
    """Core AI functionality untuk Gallery Assistant"""
    
    def __init__(self):
        # Set up cache directory
        base_dir = Path(__file__).resolve().parent
        self.cache_dir = base_dir / 'models_cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        print(f"Loading AI models from cache: {self.cache_dir}")
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment",
            model_kwargs={"cache_dir": self.cache_dir / 'sentiment'}
        )
        print("Sentiment analyzer loaded")
        
        # Initialize semantic model
        self.semantic_model = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2',
            cache_folder=str(self.cache_dir / 'semantic')
        )
        print("Semantic model loaded")
        
        # Initialize NER model with max_length
        tokenizer = AutoTokenizer.from_pretrained(
            "cahya/bert-base-indonesian-NER",
            cache_dir=self.cache_dir / 'ner'
        )
        model = AutoModelForTokenClassification.from_pretrained(
            "cahya/bert-base-indonesian-NER",
            cache_dir=self.cache_dir / 'ner'
        )
        self.ner_model = pipeline(
            "ner",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",
        )
        print("NER model loaded")
        
        # Gunakan intents dari GalleryResponses
        self.intents = GalleryResponses.INTENTS
        
        # Pre-defined responses dari GalleryResponses
        self.responses = GalleryResponses.RESPONSES
        
        # Pre-compute embeddings
        print("Computing embeddings...")
        self.embeddings = self._compute_embeddings()
        print("Embeddings computed")
        
        # Forbidden topics
        self.forbidden_topics = [
            'password', 'admin', 'login', 'database', 'server',
            'backend', 'code', 'sistem', 'system', 'private'
        ]
        
        print("AI Core initialization completed")

    def _compute_embeddings(self):
        """Pre-compute embeddings untuk semua responses"""
        embeddings = {}
        for intent, lang_responses in self.responses.items():
            embeddings[intent] = {}
            for lang, response in lang_responses.items():
                embeddings[intent][lang] = self.semantic_model.encode(response['text'])
        return embeddings

    def analyze_text(self, text, conversation_history=None):
        """Analyze text comprehensively with conversation context"""
        try:
            # Language detection - improve accuracy
            text_lower = text.lower()
            id_words = ['apa', 'bagaimana', 'cara', 'lihat', 'foto', 'gambar', 'bisa', 'tolong']
            is_indonesian = any(word in text_lower for word in id_words)
            language = 'id' if is_indonesian else 'en'

            # Sentiment analysis
            sentiment = self._convert_to_native_types(self.sentiment_analyzer(text)[0])

            # NER dengan handling max_length - Perbaikan disini
            try:
                # Batasi panjang teks untuk NER
                max_length = 128
                truncated_text = ' '.join(text.split()[:max_length])
                entities = self._convert_to_native_types(
                    self.ner_model(truncated_text)
                )
            except Exception as e:
                print(f"NER error: {str(e)}")
                entities = []

            # Intent classification - Disederhanakan
            intent = self.classify_intent(text)
            confidence = 0.8  # Default confidence

            # Determine if clarification is needed
            requires_clarification = confidence < 0.4
            
            return {
                'language': language,
                'sentiment': sentiment,
                'entities': entities,
                'intent': intent,
                'confidence': confidence,
                'requires_clarification': requires_clarification
            }
            
        except Exception as e:
            print(f"Error in analyze_text: {str(e)}")
            # Return default values jika error
            return {
                'language': 'id',
                'sentiment': {'label': '3 stars', 'score': 0.5},
                'entities': [],
                'intent': 'general',
                'confidence': 0.5,
                'requires_clarification': False
            }

    def _advanced_intent_classification(self, text):
        """Classify intent with advanced analysis"""
        text_lower = text.lower()
        
        # Check dynamic intents first
        dynamic_patterns = {
            'popular_photos': [
                'populer', 'popular', 'like terbanyak', 'most liked', 
                'foto dengan like', 'photo with most likes', 'foto yang disukai',
                'photo dengan like', 'foto paling banyak like'
            ],
            # 'latest_photos': ['foto terbaru', 'latest photos', 'baru ditambahkan'],
            # 'latest_albums': ['album terbaru', 'latest albums', 'koleksi baru'],
            # 'latest_informasi': ['informasi terbaru', 'info terkini', 'berita terbaru', 'latest news', 'informasi'],
            # 'latest_agenda': ['agenda terbaru', 'agenda', 'acara terbaru', 'upcoming events', 'jadwal']
        }
        
        for intent, patterns in dynamic_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return intent, 0.9
        
        # Continue with regular intent classification
        return self.classify_intent(text), 0.8

    def _analyze_semantic_context(self, text):
        """Analyze semantic context of the query"""
        # Ekstrak kata kunci dan konteks
        keywords = set(word.lower() for word in text.split())
        gallery_related = {
            'gallery': ['foto', 'gambar', 'album', 'galeri', 'photo', 'image', 'picture'],
            'action': ['lihat', 'cari', 'tampilkan', 'view', 'search', 'show'],
            'category': ['kategori', 'jenis', 'tipe', 'category', 'type'],
            'help': ['bantuan', 'help', 'panduan', 'guide']
        }
        
        context_scores = {}
        for context, related_words in gallery_related.items():
            score = sum(1 for word in keywords if word in related_words)
            context_scores[context] = score / len(keywords) if keywords else 0
        
        return context_scores

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
        elif hasattr(obj, 'item'):  # For PyTorch tensors
            return obj.item()
        return obj

    def classify_intent(self, text):
        """Classify intent of the text"""
        text_lower = text.lower()
        
        # Find best matching intent
        best_intent = None
        highest_score = 0
        
        for intent, patterns in self.intents.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > highest_score:
                highest_score = score
                best_intent = intent
                
        return best_intent or 'general'

    def get_best_response(self, text, language, intent):
        """Get best response based on semantic similarity"""
        try:
            return GalleryResponses.get_response(intent, language), 1.0
        except Exception as e:
            print(f"Error in get_best_response: {str(e)}")
            return GalleryResponses.get_error_response(language), 0

    def is_safe_query(self, text):
        """Check if query is safe to respond"""
        return not any(topic in text.lower() for topic in self.forbidden_topics)

    def get_suggested_questions(self, text, language):
        """Get context-aware suggested questions"""
        suggestions = GalleryResponses.get_suggested_questions(language)
        
        # Get embeddings
        text_embedding = self.semantic_model.encode(text)
        suggestion_embeddings = self.semantic_model.encode(suggestions)
        
        # Calculate similarities
        similarities = torch.nn.functional.cosine_similarity(
            torch.tensor(text_embedding).unsqueeze(0),
            torch.tensor(suggestion_embeddings),
            dim=1
        )
        
        # Get top 3 most relevant suggestions
        top_indices = torch.topk(similarities, k=3).indices
        return [suggestions[idx] for idx in top_indices]