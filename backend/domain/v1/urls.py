from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

domain_router_v1 = DefaultRouter(trailing_slash="optional")
domain_router_v1.register("tags/?", TagViewSet, basename="tags")
domain_router_v1.register("recipes/?", RecipeViewSet, basename="recipes")
domain_router_v1.register("ingredients/?", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("", include(domain_router_v1.urls)),
]
