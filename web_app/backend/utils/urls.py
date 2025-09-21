from rest_framework.routers import DefaultRouter
from .views import UtilsViewSet

router = DefaultRouter()
router.register(r"", UtilsViewSet, basename="utils")

urlpatterns = router.urls
