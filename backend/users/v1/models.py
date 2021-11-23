from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRoles:
    USER = "user"
    ADMIN = "admin"
    USER_ROLE_CHOICES = [
        (USER, USER),
        (ADMIN, ADMIN),
    ]


class User(AbstractUser):
    role = models.CharField(
        max_length=150,
        choices=UserRoles.USER_ROLE_CHOICES,
        default=UserRoles.USER,
        verbose_name="User role",
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="User E-Mail",
    )

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="followings",
        verbose_name="Follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="followers",
        verbose_name="Following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "author"],
                name="unique_follow_pair"
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("author")),
                name="follower_and_author_can_not_be_equal",
            ),
        ]
