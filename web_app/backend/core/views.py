"""Shim module that re-exports handlers split into separate modules.

This file previously contained many view functions and viewsets. To keep the
module surface identical for Django routing, we now import the symbols from
their new locations and expose them here.
"""

from .chathistory import download_chat_markdown
from .api_storage import (
    is_valid_sqlite,
    sanitize_and_replace,
    save_to_model,
    OAuthRestrictedModelViewSet,
    FilesViewSet,
)
from .api_chat import APIKeysViewSet, UsageView, chats_view

__all__ = [
    "download_chat_markdown",
    "is_valid_sqlite",
    "sanitize_and_replace",
    "save_to_model",
    "OAuthRestrictedModelViewSet",
    "FilesViewSet",
    "APIKeysViewSet",
    "UsageView",
    "chats_view",
]
