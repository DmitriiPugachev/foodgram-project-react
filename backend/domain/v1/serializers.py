from django.contrib.auth import get_user_model
from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators
from rest_framework.relations import SlugRelatedField

from users.v1.serializers import UserSerializer
from recipe.models import (
    Tag,
    Ingredient,
    IngredientPortion,
    IsFavorited,
    IsInShoppingCart,
    Recipe,
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
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class IngredientPortionSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source="ingredient", queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientPortion
        fields = ("id", "amount")


class IngredientPortionGetSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()

    def get_ingredient(self, obj):
        return IngredientSerializer(Ingredient.objects.filter(id=obj.ingredient))

    class Meta:
        model = IngredientPortion
        fields = ("ingredient", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientPortionSerializer(many=True)

    def to_representation(self, value):
        self.fields["tags"] = TagSerializer(many=True)
        return super().to_representation(value)

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        setattr(recipe, "tags", *tags_data)
        for ingredient in ingredients_data:
            IngredientPortion.objects.get_or_create(
                ingredient=ingredient["ingredient_id"],
                recipe=recipe.id,
                amount=ingredient["amount"],
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        instance.tags.clear()
        setattr(instance, **validated_data)
        setattr(instance, "tags", *tags_data)
        IngredientPortion.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_data:
            IngredientPortion.objects.get_or_create(
                ingredient=ingredient["ingredient_id"],
                recipe=instance.id,
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
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("id", "author")


class RecipeGetSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_author(self,obj):
        return UserSerializer(User.objects.filter(username=obj.author.userename))

    def get_ingredients(self, obj):
        return IngredientPortionGetSerializer(IngredientPortion.objects.filter(recipe=obj).all(), many=True)

    def get_is_favorited(self, obj):
        is_favorited = False
        current_user = self.context["request"].user
        if IsFavorited.objects.filter(recipe=obj, follower=current_user):
            is_favorited = True
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        is_in_shopping_cart = False
        current_user = self.context["request"].user
        if IsInShoppingCart.objects.filter(recipe=obj, customer=current_user):
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
