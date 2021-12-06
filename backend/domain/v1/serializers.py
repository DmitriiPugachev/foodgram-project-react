from django.contrib.auth import get_user_model
from rest_framework import serializers, validators
from drf_extra_fields.fields import Base64ImageField

from users.v1.serializers import CustomGetUserSerializer
from recipe.models import (
    Tag,
    Ingredient,
    IngredientPortion,
    IsFavorited,
    IsInShoppingCart,
    Recipe,
    RecipeTag,
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_uint")
        read_only_fields = ("id", "name", "measurement_uint")


class IsFavoritedSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsFavorited
        fields = ("follower", "recipe")


class IsInShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsInShoppingCart
        fields = ("customer", "recipe")


class IngredientPortionSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(source="ingredient.name")
    measurement_unit = serializers.StringRelatedField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientPortion
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="tag", queryset=Tag.objects.all()
    )
    name = serializers.StringRelatedField(source="tag.name")
    color = serializers.StringRelatedField(source="tag.color")
    slug = serializers.StringRelatedField(source="tag.slug")

    class Meta:
        model = RecipeTag
        fields = ("id", "name", "color", "slug")


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomGetUserSerializer(read_only=True)
    ingredients = IngredientPortionSerializer(
        many=True, source="ingredients_in_portion"
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients_in_portion")
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            RecipeTag.objects.get_or_create(recipe=recipe, tag=tag)
        for ingredient in ingredients_data:
            IngredientPortion.objects.get_or_create(
                ingredient=ingredient["ingredient"],
                recipe=recipe,
                amount=ingredient["amount"],
            )
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients_in_portion")
        RecipeTag.objects.filter(recipe=instance).delete()
        IngredientPortion.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        for tag in tags_data:
            RecipeTag.objects.get_or_create(recipe=instance, tag=tag)
        for ingredient in ingredients_data:
            IngredientPortion.objects.get_or_create(
                ingredient=ingredient["ingredient"],
                recipe=instance,
                amount=ingredient["amount"],
            )
        return instance

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "ingredients",
            "name",
            "text",
            "cooking_time",
            "image",
        )
        read_only_fields = ("id", "author")


class RecipeGetSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_author(self, obj):
        return CustomGetUserSerializer(
            User.objects.filter(username=obj.author.username).all(), context=self.context, many=True,
        ).data

    def get_ingredients(self, obj):
        return IngredientPortionSerializer(
            IngredientPortion.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_tags(self, obj):
        return RecipeTagSerializer(
            RecipeTag.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        is_favorited = False
        current_user = self.context["request"].user
        if IsFavorited.objects.filter(recipe=obj, follower=current_user.id):
            is_favorited = True
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        is_in_shopping_cart = False
        current_user = self.context["request"].user
        if IsInShoppingCart.objects.filter(
            recipe=obj, customer=current_user.id
        ):
            is_in_shopping_cart = True
        return is_in_shopping_cart

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("id", "author")
