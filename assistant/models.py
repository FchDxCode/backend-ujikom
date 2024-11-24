# assistant/models.py
from django.db import models
import uuid

class AssistantContext(models.Model):
    """Model untuk menyimpan context memory dari percakapan"""
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    context = models.JSONField(default=dict)
    conversation_history = models.JSONField(default=list)
    conversation_turns = models.IntegerField(default=0)
    last_intent = models.CharField(max_length=50, null=True)
    last_topic = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

class ChatHistory(models.Model):
    """Model untuk menyimpan history chat"""
    session_id = models.UUIDField()
    question = models.TextField()
    answer = models.TextField()
    language = models.CharField(max_length=10)
    sentiment = models.CharField(max_length=20)
    intent = models.CharField(max_length=50)
    entities = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class InteractionLog(models.Model):
    """Model untuk mencatat dan menganalisis interaksi"""
    session_id = models.UUIDField()
    question = models.TextField()
    answer = models.TextField()
    language = models.CharField(max_length=10)
    sentiment = models.CharField(max_length=20)
    intent = models.CharField(max_length=50)
    confidence_score = models.FloatField()
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']