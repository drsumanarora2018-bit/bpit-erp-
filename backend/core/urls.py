from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import DepartmentViewSet, UserViewSet, MeView, MyTokenObtainPairView

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
