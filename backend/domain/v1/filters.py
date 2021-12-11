from rest_framework import filters
from django_filters.filters import AllValuesMultipleFilter, CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from recipe.models import Recipe, Ingredient


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name="tags__slug")
    author = NumberFilter(field_name="author__id")

    class Meta:
        model = Recipe
        fields = ("tags", )


class IngredientFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ("name", )


