from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework.response import Response

from api.v1.filters import IngredientFilter, RecipeFilter
from api.v1.mixins import CreateListRetrieveViewSet
from api.v1.paginators import PageSizeInParamsPagination
from api.v1.permissions import (CustomIsAuthenticated, IsAdmin, IsOwner,
                                IsSafeMethod, IsSuperUser)
from api.v1.serializers import (CustomCreateUserSerializer,
                                CustomGetUserSerializer, FollowSerializer,
                                IngredientSerializer, IsFavoritedSerializer,
                                IsInShoppingCartSerializer,
                                PasswordUpdateSerializer,
                                RecipeCreateSerializer, RecipeGetSerializer,
                                TagSerializer)
from recipe.models import (Ingredient, IngredientPortion, IsFavorited,
                           IsInShoppingCart, Recipe, Tag)
from users.models import Follow

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsSafeMethod]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageSizeInParamsPagination
    permission_classes = [
        CustomIsAuthenticated & (IsAdmin | IsSuperUser | IsOwner)
        | IsSafeMethod
    ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user, partial=False)

    def add(self, request, model, serializer_class, location, **kwargs):
        user_me = request.user
        recipe = get_object_or_404(Recipe, id=kwargs["recipes_id"])
        if request.method == "GET":
            data = {"user": user_me.id, "recipe": recipe.id}
            context = {"request": request}
            serializer = serializer_class(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not model.objects.filter(user=user_me, recipe=recipe).exists():
                return Response(
                    {"detail": f"There is no this recipe in {location}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.filter(user=user_me, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get", "delete"],
        url_path=r"(?P<recipes_id>\d+)/favorite",
        url_name="favorite",
        permission_classes=[CustomIsAuthenticated],
        pagination_class=None,
    )
    def favorite(self, request, **kwargs):
        return self.add(
            request=request,
            model=IsFavorited,
            serializer_class=IsFavoritedSerializer,
            location="favorites",
            **kwargs,
        )

    @action(
        detail=False,
        methods=["get", "delete"],
        url_path=r"(?P<recipes_id>\d+)/shopping_cart",
        url_name="shopping_cart",
        permission_classes=[CustomIsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        return self.add(
            request=request,
            model=IsInShoppingCart,
            serializer_class=IsInShoppingCartSerializer,
            location="cart",
            **kwargs,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
        permission_classes=[CustomIsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user_me = request.user
        shopping_cart = "Мой список покупок: \n"
        shopping_queryset = (
            IngredientPortion.objects.filter(recipe__customers__user=user_me)
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        for ingredient_item in shopping_queryset:
            shopping_cart += (
                f"{ingredient_item['ingredient__name']} "
                f"- {ingredient_item['amount']} "
                f"({ingredient_item['ingredient__measurement_unit']})\n"
            )
        response = HttpResponse(
            shopping_cart, "Content-Type: application/txt"
        )
        response[
            "Content-Disposition"
        ] = "attachment; filename='Shopping cart'"
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsSafeMethod]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


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
        user_me = request.user
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
            if not Follow.objects.filter(
                follower=user_me, author=author
            ).exists():
                return Response(
                    {"detail": "There is no this author in your followings."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Follow.objects.filter(follower=user_me, author=author).delete()
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
        queryset = Follow.objects.filter(follower=follower)
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
        serializer = PasswordUpdateSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
