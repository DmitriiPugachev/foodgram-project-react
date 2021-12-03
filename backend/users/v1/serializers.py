from django.contrib.auth import get_user_model
from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers, validators
from rest_framework.relations import SlugRelatedField

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("username", "email")
