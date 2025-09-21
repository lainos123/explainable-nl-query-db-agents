from rest_framework import serializers
from .models import Files, Sessions, Chats, APIKeys

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['id', 'file', 'time']

class SessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sessions
        fields = ['id', 'user', 'start_time']

class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = ['id', 'time', 'user', 'agent', 'prompt', 'response']


class APIKeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKeys
        fields = ['id', 'user', 'api_key']