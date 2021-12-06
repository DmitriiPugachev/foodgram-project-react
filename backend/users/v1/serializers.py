from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers, validators

from users.models import Follow

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("follower", "author")


class CustomGetUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        is_subscribed = False
        user_me = self.context["request"].user
        if Follow.objects.filter(author=obj, follower=user_me):
            is_subscribed = True
        return is_subscribed

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_subscribed")


class CustomCreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "id", "password")
