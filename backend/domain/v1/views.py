from django.contrib.auth import get_user_model
from django.db.models import Sum
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
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from users.v1.permissions import (
    CustomIsAuthenticated,
    IsAdmin,
    IsOwner,
    IsSafeMethod,
    IsSuperUser,
)
from domain.v1.serializers import (
    IngredientSerializer,
    IsFavoritedSerializer,
    IsInShoppingCartSerializer,
    RecipeCreateSerializer,
    RecipeGetSerializer,
    TagSerializer,
)
from domain.v1.paginators import PageSizeInParamsPagination

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsSafeMethod]


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageSizeInParamsPagination
    permission_classes = [
        CustomIsAuthenticated & (IsAdmin | IsSuperUser | IsOwner)
        | IsSafeMethod
    ]

    def get_queryset(self):
        # RETRIEVE = "retrieve"
        # DESTROY = "destroy"
        # UPDATE = "update"
        # ACTIONS_WITHOUT_FILTRATION = [RETRIEVE, DESTROY, UPDATE]
        query_params = self.request.query_params
        user_me = self.request.user
        queryset = Recipe.objects.all()
        # if self.action in ACTIONS_WITHOUT_FILTRATION:
        #     queryset = Recipe.objects.all()
        if query_params.__contains__( "is_favorited"):
            queryset = queryset.filter(followers__follower=user_me).all()
            if query_params.__contains__("tags"):
                queryset = queryset.filter(tags__slug__in=query_params.getlist("tags", "")).all().distinct()
        elif query_params.__contains__("is_in_shopping_cart"):
            queryset = queryset.filter(customers__customer=user_me).all()
        elif query_params.__contains__("author"):
            queryset = queryset.filter(author=query_params.get("author")).all()
            if query_params.__contains__("tags"):
                queryset = queryset.filter(tags__slug__in=query_params.getlist("tags", "")).distinct()
        elif query_params.__contains__("tags"):
            queryset = queryset.filter(tags__slug__in=query_params.getlist("tags", "")).distinct()
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
        pagination_class=None
    )
    def favorite(self, request, **kwargs):
        user_me = request.user
        recipe = get_object_or_404(Recipe, id=kwargs["recipes_id"])
        if request.method == "GET":
            favorited_data = {"follower": user_me.id, "recipe": recipe.id}
            context = {"request": request}
            serializer = IsFavoritedSerializer(data=favorited_data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not IsFavorited.objects.filter(follower=user_me, recipe=recipe):
                return Response(
                    {"detail": "There is no this recipe in your favorites."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            IsFavorited.objects.filter(
                follower=user_me, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        if request.method == "GET":
            added_data = {"customer": user_me.id, "recipe": recipe.id}
            context = {"request": request}
            serializer = IsInShoppingCartSerializer(data=added_data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not IsInShoppingCart.objects.filter(customer=user_me, recipe=recipe):
                return Response(
                    {"detail": "There is no this recipe in your cart."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            IsInShoppingCart.objects.filter(
                customer=user_me, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
