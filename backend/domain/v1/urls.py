from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteViewSet,
    IngredientsViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
    download_shopping_cart,
)

domain_router_v1 = DefaultRouter(trailing_slash="optional")
domain_router_v1.register("tags/?", TagViewSet, basename="tags")
domain_router_v1.register("recipes/?", RecipeViewSet, basename="recipes")
domain_router_v1.register("ingredients/?", IngredientsViewSet, basename="ingredients")
domain_router_v1.register(
    r"recipes/(?P<recipes_id>\d+)/shopping_cart/",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
domain_router_v1.register(
    r"recipes/(?P<recipes_id>\d+)/favorite/",
    FavoriteViewSet,
    basename="favorite",
)

urlpatterns = [
    path(
        "recipes/download_shopping_cart/",
        download_shopping_cart,
        name="download_shopping_cart",
    ),
    path("", include(domain_router_v1.urls)),
]
