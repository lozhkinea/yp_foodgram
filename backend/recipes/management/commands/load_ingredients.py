'''
Скрипт для загрузки списка ингредиентов из CSV-файла.
'''
from csv import DictReader
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из csv-файлов'

    def add_arguments(self, parser):
        parser.add_argument('filepath')

    def handle(self, *args, **options):
        COL1, COL2 = 'name', 'measurement_unit'

        Ingredient.objects.all().delete()
        fieldnames = [COL1, COL2]
        csv_filename = Path(options['filepath'])
        if not csv_filename.exists():
            raise CommandError('Файл "%s" не найден' % options['filepath'])
        with open(csv_filename, newline='') as csv_file:
            reader = DictReader(csv_file, fieldnames)
            for row in reader:
                instance = Ingredient.objects.create(
                    name=row[COL1], measurement_unit=row[COL2]
                )
                instance.save
                print(f'{instance.id}, {row[COL1]}, {row[COL2]}')
