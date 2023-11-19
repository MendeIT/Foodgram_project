import csv
import os

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from recipes.models import Ingredient
from foodgram_project.settings import BASE_DIR


class Command(BaseCommand):
    help = "Load model Ingredinets in DB (.csv)."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('######## START LOAD ########'))
        csv_file = os.path.join(BASE_DIR, 'ingredients.csv')
        try:
            with open(file=csv_file, mode='r', encoding='utf-8') as f:
                rows = csv.reader(f)
                for row in tqdm(rows):
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'Файл CSV не найден: {e}'))
        except Ingredient.DoesNotExist as e:
            raise CommandError(f'Ингредиент не существует: {e}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Что-то пошло не так: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('######## SUCCESS ########'))
