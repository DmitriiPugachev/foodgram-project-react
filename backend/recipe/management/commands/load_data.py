import csv

from django.core.management.base import BaseCommand

from recipe.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients data to DB"

    def handle(self, *args, **options):
        with open("recipe/data/ingredients.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                name, measurement_uint = row
                Ingredient.objects.get_or_create(name=name, measurement_uint=measurement_uint)
