"""Recipe models description."""


from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Tag model description."""
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name="Tag name",
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Tag color",
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Tag slug",
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        """Returns string view of a name filed."""
        return self.name


class Ingredient(models.Model):
    """Ingredient model description."""
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Ingredient name",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Measurement unit",
    )

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"

    def __str__(self):
        """Returns string view for name and measurement_unit fields."""
        return "{}, {}".format(self.name, self.measurement_unit)


class Recipe(models.Model):
    """Recipe model description."""
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        verbose_name="Tags",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="recipes",
        verbose_name="Recipe author",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientPortion",
        verbose_name="Ingredients",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Recipe name",
    )
    image = models.ImageField(
        verbose_name="Recipe image",
    )
    text = models.CharField(
        max_length=1000,
        verbose_name="Recipe description",
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                1, message="Cooking time can not be less than 1 minute."
            ),
        ),
        verbose_name="Recipe cooking time, minutes",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Recipe publication date",
    )

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ["-pub_date"]

    def __str__(self):
        """Returns string view for a name field."""
        return self.name


class IngredientPortion(models.Model):
    """IngredientPortion model description."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="ingredients_in_portion",
        verbose_name="Recipe with portion",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="portions",
        verbose_name="Ingredient in portion",
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1, message="Amount can not be less than 1."),
        ),
        verbose_name="Portion size",
    )

    class Meta:
        verbose_name = "Portion"
        verbose_name_plural = "Portions"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_portion_pair"
            ),
        ]


class IsFavorited(models.Model):
    """IsFavorited model description."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="favorited_recipes",
        verbose_name="Follower",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="followers",
        verbose_name="Favorited recipe",
    )

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorited_pair"
            ),
        ]


class IsInShoppingCart(models.Model):
    """IsInShoppingCart model description."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="in_cart_recipes",
        verbose_name="Customer",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="customers",
        verbose_name="Recipe in cart",
    )

    class Meta:
        verbose_name = "Shopping cart"
        verbose_name_plural = "Shopping carts"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_in_cart_pair"
            ),
        ]
