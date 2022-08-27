import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда 'load_ingredients' загружает ингредиенты
    в базу из csv файла.
    """

    def handle(self, *args, **options):
        self.import_ingredients()
        print('Загрузка завершена.')

    def import_ingredients(self, file='ingredients.csv'):
        print(f'Загрузка {file}...')
        file_path = f'../data/{file}'
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for data in reader:
                status, created = Ingredient.objects.update_or_create(
                    name=data[0],
                    measurement_unit=data[1]
                )
