# Generated by Django 2.2.6 on 2021-12-11 16:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, verbose_name='Ingredient name')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Measurement unit')),
            ],
        ),
        migrations.CreateModel(
            name='IngredientPortion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Portion size')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portions', to='recipe.Ingredient', verbose_name='Ingredient in portion')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, unique=True, verbose_name='Tag name')),
                ('color', models.CharField(blank=True, max_length=7, null=True, unique=True, verbose_name='Tag color')),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Tag slug')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Recipe name')),
                ('image', models.ImageField(upload_to='', verbose_name='Recipe image')),
                ('text', models.CharField(max_length=1000, verbose_name='Recipe description')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Recipe cooking time, minutes')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Recipe publication date')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Recipe author')),
                ('ingredients', models.ManyToManyField(through='recipe.IngredientPortion', to='recipe.Ingredient', verbose_name='Ingredients')),
                ('tags', models.ManyToManyField(db_index=True, to='recipe.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='IsInShoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_cart_recipes', to=settings.AUTH_USER_MODEL, verbose_name='Customer')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customers', to='recipe.Recipe', verbose_name='Favorited recipe')),
            ],
        ),
        migrations.CreateModel(
            name='IsFavorited',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_recipes', to=settings.AUTH_USER_MODEL, verbose_name='Follower')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='recipe.Recipe', verbose_name='Favorited recipe')),
            ],
        ),
        migrations.AddField(
            model_name='ingredientportion',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_in_portion', to='recipe.Recipe', verbose_name='Recipe with portion'),
        ),
        migrations.AddConstraint(
            model_name='isinshoppingcart',
            constraint=models.UniqueConstraint(fields=('customer', 'recipe'), name='unique_in_cart_pair'),
        ),
        migrations.AddConstraint(
            model_name='isfavorited',
            constraint=models.UniqueConstraint(fields=('follower', 'recipe'), name='unique_favorited_pair'),
        ),
    ]
