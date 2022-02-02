"""API v.1 custom filters."""


from django_filters.filters import (AllValuesMultipleFilter, BooleanFilter,
                                    CharFilter, NumberFilter)
from django_filters.rest_framework import FilterSet

from recipe.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    """Recipe custom filter."""
    tags = AllValuesMultipleFilter(field_name="tags__slug")
    author = NumberFilter(field_name="author__id")
    is_favorited = BooleanFilter(
        field_name="followers__user",
        method="get_is_added",
        label="Is favorited",
    )
    is_in_shopping_cart = BooleanFilter(
        field_name="customers__user",
        method="get_is_added",
        label="Is in shopping cart",
    )

    def get_is_added(self, queryset, field_name, value):
        """Definition get_is_added method."""
        if value:
            user_me = self.request.user
            kwargs = {field_name: user_me}
            queryset = queryset.filter(**kwargs)
            return queryset

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")


class IngredientFilter(FilterSet):
    """Ingredient custom filter."""
    name = CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
