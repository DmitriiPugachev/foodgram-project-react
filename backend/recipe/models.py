from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
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

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Ingredient name",
    )
    measurement_uint = models.CharField(
        max_length=200,
        verbose_name="Measurement unit",
    )

    def __str__(self):
        return "{}, {}".format(self.name, self.measurement_uint)


class Recipe(models.Model):
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
        verbose_name="Ingredients with a portion",
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
        validators=(MinValueValidator(1),),
        verbose_name="Recipe cooking time, minutes",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Recipe publication date",
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class IngredientPortion(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="ingredient_in_portion",
        verbose_name="Recipe with portion",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="portion",
        verbose_name="Ingredient in portion",
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        verbose_name="Portion size",
    )


class IsFavorited(models.Model):
    follower = models.ForeignKey(
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
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "recipe"],
                name="unique_favorited_pair"
            ),
        ]


class IsInShoppingCart(models.Model):
    customer = models.ForeignKey(
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
        verbose_name="Favorited recipe",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "recipe"],
                name="unique_in_cart_pair"
            ),
        ]
