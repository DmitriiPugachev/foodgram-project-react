from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipe.models import (
    Ingredient,
    IngredientPortion,
    IsFavorited,
    IsInShoppingCart,
    Recipe,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from users.v1.permissions import (
    CustomIsAuthenticated,
    IsAdmin,
    IsOwner,
    IsSafeMethod,
    IsSuperUser,
)

from .serializers import (
    IngredientSerializer,
    IsFavoritedSerializer,
    IsInShoppingCartSerializer,
    RecipeCreateSerializer,
    RecipeGetSerializer,
    TagSerializer,
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsSafeMethod]


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = [
        CustomIsAuthenticated & (IsAdmin | IsSuperUser | IsOwner)
        | IsSafeMethod
    ]

    def get_queryset(self):
        query_params = self.request.query_params
        user_me = self.request.user
        queryset = Recipe.objects.none()
        if query_params.__contains__(
            "is_favorited"
        ) and query_params.__contains__("tags"):
            queryset = (
                Recipe.objects.all()
                .filter(followers__follower=user_me)
                .filter(tags__slug__in=query_params.getlist("tags", ""))
                .distinct()
            )
        elif query_params.__contains__(
            "is_in_shopping_cart"
        ) and query_params.__contains__("tags"):
            queryset = (
                Recipe.objects.all()
                .filter(customers__customer=user_me)
                .filter(tags__slug__in=query_params.getlist("tags", ""))
                .distinct()
            )
        elif query_params.__contains__(
            "author"
        ) and query_params.__contains__("tags"):
            queryset = (
                Recipe.objects.all()
                .filter(author=query_params.get("author"))
                .filter(tags__slug__in=query_params.getlist("tags", ""))
                .distinct()
            )
        elif query_params.__contains__("tags"):
            queryset = (
                Recipe.objects.all()
                .filter(tags__slug__in=query_params.getlist("tags", ""))
                .distinct()
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user, partial=False)

    @action(
        detail=False,
        methods=["get", "delete"],
        url_path=r"(?P<recipes_id>\d+)/favorite",
        url_name="favorite",
        permission_classes=[CustomIsAuthenticated],
    )
    def favorite(self, request, **kwargs):
        user_me = request.user
        recipe = get_object_or_404(Recipe, id=kwargs["recipes_id"])
        favorited = IsFavorited.objects.filter(
            follower=user_me, recipe=recipe
        ).exists()
        if request.method == "GET" and not favorited:
            favorited_data = {"follower": user_me.id, "recipe": recipe.id}
            serializer = IsFavoritedSerializer(data=favorited_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE" and favorited:
            IsFavorited.objects.filter(
                follower=user_me, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Action is already done!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["get", "delete"],
        url_path=r"(?P<recipes_id>\d+)/shopping_cart",
        url_name="shopping_cart",
        permission_classes=[CustomIsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        user_me = request.user
        recipe = get_object_or_404(Recipe, id=kwargs["recipes_id"])
        added = IsInShoppingCart.objects.filter(
            customer=user_me, recipe=recipe
        ).exists()
        if request.method == "GET" and not added:
            added_data = {"customer": user_me.id, "recipe": recipe.id}
            serializer = IsInShoppingCartSerializer(data=added_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE" and added:
            IsInShoppingCart.objects.filter(
                customer=user_me, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Action is already done!"},
            status=status.HTTP_400_BAD_REQUEST,
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
            IngredientPortion.objects.filter(
                recipe__customers__customer=user_me
            )
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
    serializer_class = IngredientSerializer
    permission_classes = [IsSafeMethod]

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        if self.request.query_params.get("name"):
            queryset = Ingredient.objects.filter(
                name__startswith=self.request.query_params.get("name"),
            )
        return queryset
