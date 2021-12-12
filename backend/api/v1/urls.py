from django.urls import include, path
from rest_framework.routers import DefaultRouter

from domain.v1.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.v1.views import CustomUserViewSet

router_v1 = DefaultRouter(trailing_slash="optional")
router_v1.register("users", CustomUserViewSet, basename="users")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router_v1.urls)),
]
