from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS

from recipe.models import Tag, Ingredient, IngredientPortion, IsFavorited, IsInShoppingCart, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeCreateSerializer, RecipeGetSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    pass


def download_shopping_cart():
    pass

class FavoriteViewSet(viewsets.ModelViewSet):
    pass


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
