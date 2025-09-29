from rest_framework import serializers
from .models import Files, APIKeys


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ["id", "user", "file", "database", "time"]


# Chats model removed; frontend stores chat session in localStorage and can POST to download endpoint


class APIKeysSerializer(serializers.ModelSerializer):
    has_key = serializers.SerializerMethodField(read_only=True)
    api_key = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = APIKeys
        fields = ["id", "user", "has_key", "api_key"]

    def get_has_key(self, obj):
        return bool(obj.api_key)

    def get_api_key(self, obj):
        """Return masked version of API key for display"""
        if obj.api_key:
            # Show first 8 and last 4 characters
            return obj.api_key[:8] + "..." + obj.api_key[-4:]
        return None
