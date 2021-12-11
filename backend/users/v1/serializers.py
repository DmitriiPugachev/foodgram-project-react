from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipe.models import Recipe
from rest_framework import serializers, validators

from users.models import Follow

User = get_user_model()


class FollowingRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(
        read_only=True
    )
    follower = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all()
    )
    author = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all()
    )
    email = serializers.StringRelatedField(
        read_only=True, source="author.email"
    )
    username = serializers.StringRelatedField(
        read_only=True, source="author.username"
    )
    first_name = serializers.StringRelatedField(
        read_only=True, source="author.first_name"
    )
    last_name = serializers.StringRelatedField(
        read_only=True, source="author.last_name"
    )
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
    )
    recipes = serializers.SerializerMethodField(
        read_only=True,
    )
    recipe_count = serializers.SerializerMethodField(
        read_only=True,
    )

    def get_is_subscribed(self, obj):
        is_subscribed = False
        user_me = get_object_or_404(
            User, username=self.context["request"].user.username
        )
        if Follow.objects.filter(author=obj.author, follower=user_me):
            is_subscribed = True
        return is_subscribed

    def get_recipes(self, obj):
        if self.context["request"].query_params.__contains__("recipes_limit"):
            recipes_limit = int(self.context["request"].query_params.get("recipes_limit"))
            return FollowingRecipesSerializer(
                Recipe.objects.filter(author=obj.author).all()[:recipes_limit], many=True
            ).data
        else:
            return FollowingRecipesSerializer(
                Recipe.objects.filter(author=obj.author).all(), many=True
            ).data

    def get_recipe_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_id(self, obj):
        return obj.author.id

    class Meta:
        model = Follow
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipe_count",
            "follower",
            "author",
        )


class CustomGetUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        is_subscribed = False
        user_me = self.context["request"].user
        if Follow.objects.filter(author=obj, follower=user_me.id):
            is_subscribed = True
        return is_subscribed

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class CustomCreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "id",
            "password",
        )


class PasswordUpdateSerializer(UserCreateSerializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, data):
        user_me = get_object_or_404(
            User, username=self.context["request"].user.username
        )
        current_password = data["current_password"]
        if not user_me.check_password(current_password):
            raise validators.ValidationError(
                "Current password is not correct!"
            )
        return data

    def create(self, validated_data):
        user_me = get_object_or_404(
            User, username=self.context["request"].user.username
        )
        new_password = validated_data.pop("new_password")
        user_me.set_password(new_password)
        user_me.save()
        return user_me

    class Meta:
        model = User
        fields = ("new_password", "current_password")
