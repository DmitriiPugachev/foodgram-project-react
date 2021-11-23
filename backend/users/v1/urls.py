from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

users_router_v1 = DefaultRouter(trailing_slash="optional")
users_router_v1.register("users/?", CustomUserViewSet, basename="users")

urlpatterns = [
    path("", include(users_router_v1.urls)),
]
