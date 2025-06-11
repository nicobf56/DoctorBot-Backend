from rest_framework import serializers
from .models import ChatHistory, Correction, Feedback

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ['id', 'question', 'answer', 'references', 'created_at']

class CorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correction
        fields = ['id', 'chat', 'user', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'chat', 'user', 'vote', 'created_at']
        read_only_fields = ['id', 'created_at']
