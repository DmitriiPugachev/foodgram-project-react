"""Recipe admin config."""


from django.contrib import admin

from recipe.models import (Ingredient, IngredientPortion, IsFavorited,
                           IsInShoppingCart, Recipe, Tag)


class TagAdmin(admin.ModelAdmin):
    """Tag model admin config."""
    list_display = (
        "name",
        "color",
        "slug",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-empty-"
    prepopulated_fields = {"slug": ("name",)}


class IngredientAdmin(admin.ModelAdmin):
    """Ingredient model admin config."""
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-empty-"


class RecipeIngredientInline(admin.TabularInline):
    """Gives a possibility to add ingredients in Recipe objects.

    Working within IngredientAdmin interface.
    """
    model = Recipe.ingredients.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Recipe model admin config"""
    inlines = (
        RecipeIngredientInline,
    )
    list_display = (
        "author",
        "name",
        "text",
        "cooking_time",
        "count_favorited",
    )
    search_fields = ("name",)
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-empty-"

    def count_favorited(self, obj):
        """Method counts quantity of adding to favorites."""
        return IsFavorited.objects.filter(recipe_id=obj.id).count()

    count_favorited.short_description = "Favorited counter"


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientPortion)
admin.site.register(IsFavorited)
admin.site.register(IsInShoppingCart)
