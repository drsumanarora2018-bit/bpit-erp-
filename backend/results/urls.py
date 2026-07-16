from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, ResultViewSet

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet, basename="subject")
router.register(r"results", ResultViewSet, basename="result")

urlpatterns = router.urls
