from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (Ingredient, IngredientPortion, IsFavorited,
                           IsInShoppingCart, Recipe, Tag)
from rest_framework import serializers

from users.v1.serializers import CustomGetUserSerializer
from domain.v1.validators import positive_integer_in_field_validate, object_exists_validate

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IsFavoritedSerializer(serializers.ModelSerializer):
    follower = serializers.PrimaryKeyRelatedField(
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

    def validate(self, data):
        object_name = "recipe"
        object_exists = IsFavorited.objects.filter(follower=self.context["request"].user, recipe=data["recipe"]).exists()
        location = "favorites"
        return object_exists_validate(data, object_name, object_exists, location)

    class Meta:
        model = IsFavorited
        fields = ("id", "image", "name", "cooking_time", "follower", "recipe")


class IsInShoppingCartSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
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

    def validate(self, data):
        object_name = "recipe"
        object_exists = IsInShoppingCart.objects.filter(customer=self.context["request"].user, recipe=data["recipe"]).exists()
        location = "cart"
        return object_exists_validate(data, object_name, object_exists, location)

    class Meta:
        model = IsInShoppingCart
        fields = ("id", "image", "name", "cooking_time", "customer", "recipe")


class IngredientPortionSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(source="ingredient.name")
    measurement_unit = serializers.StringRelatedField(
        source="ingredient.measurement_unit"
    )

    def validate_amount(self, value):
        field_name = "Amount"
        return positive_integer_in_field_validate(value, field_name)

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

    def validate_cooking_time(self, value):
        field_name = "Cooking_time"
        return positive_integer_in_field_validate(value, field_name)

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
        is_favorited = False
        user_me = self.context["request"].user
        if IsFavorited.objects.filter(recipe=obj, follower=user_me.id):
            is_favorited = True
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        is_in_shopping_cart = False
        user_me = self.context["request"].user
        if IsInShoppingCart.objects.filter(recipe=obj, customer=user_me.id):
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
