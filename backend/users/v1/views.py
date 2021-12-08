from rest_framework import filters, mixins, status, viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .serializers import CustomGetUserSerializer, CustomCreateUserSerializer, FollowSerializer, PasswordUpdateSerializer, FollowingRecipesSerializer
from ..models import Follow
from .permissions import IsOwner, IsAdmin, IsSafeMethod, IsSuperUser, CustomIsAuthenticated
from recipe.models import Recipe

User = get_user_model()


class CreateListRetrieveViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class CustomUserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return CustomGetUserSerializer
        return CustomCreateUserSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        url_name="me",
        permission_classes=[CustomIsAuthenticated]
    )
    def me(self, request):
        user_me = get_object_or_404(User, username=self.request.user.username)
        serializer = CustomGetUserSerializer(user_me, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get", "delete"],
        url_path=r"(?P<users_id>\d+)/subscribe",
        url_name="subscribe",
        permission_classes=[CustomIsAuthenticated]
    )
    def follow(self, request, **kwargs):
        user_me = request.user
        another_user = get_object_or_404(User, id=kwargs["users_id"])
        followed = Follow.objects.filter(
            follower=user_me, author=another_user
        ).exists()
        if request.method == "GET" and not followed:
            favorited_data = {"follower": user_me.id, "author": another_user.id}
            serializer = FollowSerializer(data=favorited_data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE" and followed:
            Follow.objects.filter(follower=user_me, author=another_user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Действие уже выполнено"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        url_name="subscriptions",
        pagination_class=PageNumberPagination,
        permission_classes=[CustomIsAuthenticated]
    )
    def subscriptions(self, request):
        serializer = FollowSerializer(Follow.objects.filter(follower=request.user).all(), context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        url_path="set_password",
        url_name="set_password",
        permission_classes=[CustomIsAuthenticated]
    )
    def set_password(self, request):
        serializer = PasswordUpdateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
