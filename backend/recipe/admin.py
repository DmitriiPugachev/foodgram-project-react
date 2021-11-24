from django.contrib import admin

from .models import Tag, Ingredient, Recipe, IngredientPortion, IsFavorited, IsInShoppingCart


class TagAdmin(admin.ModelAdmin):
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
    list_display = (
        "name",
        "measurement_uint",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-empty-"


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        "author",
        "name",
        "image",
        "text",
        "cooking_time",
    )
    search_fields = ("name",)
    list_filter = ("name", "author", "tags",)
    empty_value_display = "-empty-"


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientPortion)
admin.site.register(IsFavorited)
admin.site.register(IsInShoppingCart)
