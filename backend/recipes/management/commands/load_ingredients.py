'''
Скрипт для загрузки списка ингредиентов из CSV-файла.
'''
from csv import DictReader
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


def load_ingredients():
    Ingredient.objects.all().delete()
    fieldnames = ['name', 'measurement_unit']
    csv_filename = Path.cwd().parent / 'data' / 'ingredients.csv'
    with open(csv_filename, newline='') as csv_file:
        reader = DictReader(csv_file, fieldnames)
        for row in reader:
            print(row['name'], row['measurement_unit'])
            obj = Ingredient.objects.create(
                name=row['name'], measurement_unit=row['measurement_unit']
            )
            obj.save


class Command(BaseCommand):
    help = 'Загрузка данных из csv-файлов'

    def handle(self, *args, **options):
        load_ingredients()
