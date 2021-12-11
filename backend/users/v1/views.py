from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework.response import Response

from users.v1.paginators import PageSizeInParamsPagination
from users.models import Follow
from users.v1.permissions import CustomIsAuthenticated
from users.v1.serializers import (CustomCreateUserSerializer, CustomGetUserSerializer,
                          FollowSerializer, PasswordUpdateSerializer)

User = get_user_model()


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CustomUserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = PageSizeInParamsPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return CustomGetUserSerializer
        return CustomCreateUserSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        url_name="me",
        permission_classes=[CustomIsAuthenticated],
    )
    def me(self, request):
        username = self.request.user.username
        user_me = get_object_or_404(User, username=username)
        serializer = CustomGetUserSerializer(
            user_me, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get", "delete"],
        url_path=r"(?P<users_id>\d+)/subscribe",
        url_name="subscribe",
        permission_classes=[CustomIsAuthenticated],
    )
    def follow(self, request, **kwargs):
        user_me = request.user
        users_id = kwargs["users_id"]
        author = get_object_or_404(User, id=users_id)
        if request.method == "GET":
            favorited_data = {
                "follower": user_me.id,
                "author": author.id,
            }
            context = {"request": request}
            serializer = FollowSerializer(
                data=favorited_data, context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not Follow.objects.filter(follower=user_me, author=author):
                return Response(
                    {"detail": "There is no this author in your followings."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Follow.objects.filter(
                follower=user_me, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        url_name="subscriptions",
        pagination_class=PageSizeInParamsPagination,
        permission_classes=[CustomIsAuthenticated],
    )
    def subscriptions(self, request):
        follower = request.user
        context = {"request": request}
        queryset = Follow.objects.filter(follower=follower).all()
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            context=context,
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="set_password",
        url_name="set_password",
        permission_classes=[CustomIsAuthenticated],
    )
    def set_password(self, request):
        data = request.data
        context = {"request": request}
        serializer = PasswordUpdateSerializer(
            data=data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
