from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from recipe.models import Tag, Ingredient, IngredientPortion, IsFavorited, IsInShoppingCart, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeCreateSerializer, RecipeGetSerializer, IsFavoritedSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=["get", "delete"],
        url_path=r"(?P<recipes_id>\d+)/favorite",
        url_name="favorite",
        pagination_class=PageNumberPagination,
        # permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, id=kwargs["recipes_id"])
        favorited = IsFavorited.objects.filter(
            follower=user,
            recipe=recipe
        ).exists()
        if request.method == "GET" and not favorited:
            favorited_data = {"follower": user.id, "recipe": recipe.id}
            serializer = IsFavoritedSerializer(data=favorited_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE" and favorited:
            IsFavorited.objects.filter(follower=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Действие уже выполнено"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # @action(
    #     detail=False,
    #     methods=['get', 'delete'],
    #     url_path=r'(?P<id>[\d]+)/shopping_cart',
    #     url_name='shopping_cart',
    #     pagination_class=None,
    #     # permission_classes=[IsAuthenticated]
    # )
    # def shopping_cart(self, request, **kwargs):
    #     user = request.user
    #     recipe = get_object_or_404(Recipe, id=kwargs['id'])
    #     is_added = User.objects.filter(
    #         id=user.id,
    #         shopping_carts=recipe
    #     ).exists()
    #     if request.method == 'GET' and not is_added:
    #         user.cart.recipes.add(recipe)
    #         serializer = M2MUserRecipeSerializer(recipe)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     if request.method == 'DELETE' and is_added:
    #         user.cart.recipes.remove(recipe)
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     return Response(
    #         {'detail': 'Действие уже выполнено'},
    #         status=status.HTTP_400_BAD_REQUEST
    #     )
    #
    # @action(
    #     detail=False,
    #     methods=['get'],
    #     url_path='download_shopping_cart',
    #     url_name='download_shopping_cart',
    #     pagination_class=None,
    #     # permission_classes=[IsAuthenticated]
    # )
    # def download_shopping_cart(self, request):
    #     user = request.user
    #     shopping_list = IngredientPortion.objects.filter(
    #         recipe__carts__user=user).values(
    #         'ingredient__name',
    #         'ingredient__measurement_unit'
    #     ).annotate(amount=sum('amount'))
    #     my_file = open("Shopping_list.txt", "w+")
    #     my_file.write(shopping_list)
    #     return FileResponse(my_file)


# class ShoppingCartViewSet(viewsets.ModelViewSet):
#     pass
#
#
# def download_shopping_cart():
#     pass
#
#
# class FavoriteViewSet(viewsets.ModelViewSet):
#     pass


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
