from django.db import models
from django.utils import timezone

class Conversation(models.Model):
    """A conversation between a user and an AI agent"""
    created_at = models.DateTimeField(default=timezone.now)
    agent_type = models.CharField(max_length=100, default="ad_campaign")
    
    def __str__(self):
        return f"Conversation {self.id} ({self.agent_type})"

class Message(models.Model):
    """A message in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    is_user = models.BooleanField(default=True)  # True if message is from user, False if from AI
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        sender = "User" if self.is_user else "AI"
        return f"{sender}: {self.content[:50]}" 