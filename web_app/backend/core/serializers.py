from rest_framework import serializers
from .models import APIKey, Files, Sessions, Chats, APIKey

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['id', 'database', 'file', 'time']
        extra_kwargs = {"database": {"read_only": True}}

class SessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sessions
        fields = ['id', 'user', 'start_time']

class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = ['id', 'time', 'user', 'agent', 'prompt', 'response']

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['api_key']