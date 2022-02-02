"""API v.1 URLs."""


from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                          TagViewSet)

router_v1 = DefaultRouter(trailing_slash="optional")
router_v1.register("users", CustomUserViewSet, basename="users")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router_v1.urls)),
]
