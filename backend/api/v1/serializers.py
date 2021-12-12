from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from api.v1.validators import (object_exists_validate,
                               positive_integer_in_field_validate,
                               unique_in_query_params_validate)
from recipe.models import (Ingredient, IngredientPortion, IsFavorited,
                           IsInShoppingCart, Recipe, Tag)
from users.v1.serializers import CustomGetUserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IsAddedSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Recipe.objects.all()
    )
    image = serializers.ImageField(read_only=True, source="recipe.image")
    name = serializers.StringRelatedField(
        read_only=True, source="recipe.name"
    )
    cooking_time = serializers.IntegerField(
        read_only=True, source="recipe.cooking_time"
    )


class IsFavoritedSerializer(IsAddedSerializer):
    def validate(self, data):
        return object_exists_validate(
            data=data, context=self.context, model=IsFavorited, location="favorites"
        )

    class Meta:
        model = IsFavorited
        fields = ("id", "image", "name", "cooking_time", "user", "recipe")


class IsInShoppingCartSerializer(IsAddedSerializer):
    def validate(self, data):
        return object_exists_validate(
            data=data, context=self.context, model=IsInShoppingCart, location="cart"
        )

    class Meta:
        model = IsInShoppingCart
        fields = ("id", "image", "name", "cooking_time", "user", "recipe")


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


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomGetUserSerializer(read_only=True)
    ingredients = IngredientPortionSerializer(
        many=True, source="ingredients_in_portion"
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )

    def put_data_in_fields(self, current_object, tags_data, ingredients_data):
        for tag in tags_data:
            current_object.tags.add(tag)
        for ingredient in ingredients_data:
            IngredientPortion.objects.create(
                ingredient=ingredient["ingredient"],
                recipe=current_object,
                amount=ingredient["amount"],
            )

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients_in_portion")
        recipe = Recipe.objects.create(**validated_data)
        self.put_data_in_fields(recipe, tags_data, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients_in_portion")
        instance.tags.clear()
        IngredientPortion.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.put_data_in_fields(instance, tags_data, ingredients_data)
        return instance

    def validate_tags(self, value):
        return unique_in_query_params_validate(items=value, field_name="tags", value=value)

    def validate_ingredients(self, value):
        ingredients_ids = [ingredient.get("id") for ingredient in value]
        unique_in_query_params_validate(items=ingredients_ids, field_name="ingredients", value=value)
        ingredients_amounts = [ingredient.get("amount") for ingredient in value]
        for amount in ingredients_amounts:
            positive_integer_in_field_validate(value=amount, field_name="Amount")
        return value

    def validate_cooking_time(self, value):
        return positive_integer_in_field_validate(value=value, field_name="Cooking_time")

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


class RecipeGetSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_object_exists(self, model, obj):
        object_exists = False
        user_me = self.context["request"].user
        if model.objects.filter(recipe=obj, user=user_me.id):
            object_exists = True
        return object_exists

    def get_author(self, obj):
        username = obj.author.username
        context = self.context
        return CustomGetUserSerializer(
            get_object_or_404(User, username=username),
            context=context,
        ).data

    def get_ingredients(self, obj):
        return IngredientPortionSerializer(
            IngredientPortion.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_tags(self, obj):
        return TagSerializer(
            Tag.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        return self.get_object_exists(IsFavorited, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.get_object_exists(IsInShoppingCart, obj)

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
