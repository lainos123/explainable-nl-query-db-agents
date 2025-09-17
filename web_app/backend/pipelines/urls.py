from django.urls import path
from .views import run_agent_a

urlpatterns = [
    path("agent-a/", run_agent_a),
]
