from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from recipe.models import Tag, Ingredient, IngredientPortion, IsFavorited, IsInShoppingCart, Recipe
from .serializers import TagSerializer, IngredientSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    pass


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
