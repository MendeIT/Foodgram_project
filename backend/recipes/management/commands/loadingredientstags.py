import csv
import os

from django.core.management.base import BaseCommand
from tqdm import tqdm

from foodgram_project.settings import BASE_DIR
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = "Load model Ingredinets in DB (.csv)."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('######## START LOAD ########'))
        csv_ingredients = os.path.join(BASE_DIR, 'data/ingredients.csv')
        csv_tags = os.path.join(BASE_DIR, 'data/tags.csv')
        try:
            with open(file=csv_ingredients, mode='r', encoding='utf-8') as f:
                rows = csv.reader(f)
                for row in tqdm(rows):
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
            with open(file=csv_tags, mode='r', encoding='utf-8') as f_tags:
                rows = csv.reader(f_tags)
                for row in tqdm(rows):
                    Tag.objects.get_or_create(
                        name=row[0],
                        color=row[1],
                        slug=row[2]
                    )
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'Файл CSV не найден: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Что-то пошло не так: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('######## SUCCESS ########'))
        finally:
            self.stdout.write(self.style.SUCCESS('###### FINISH LOAD ######'))
