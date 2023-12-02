import csv
import os

from django.core.management.base import BaseCommand
from tqdm import tqdm

from django.conf import settings
from users.models import User


class Command(BaseCommand):
    help = "Load 3 test users in DB (.csv)."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(
            '############### START LOAD USER ###############'
        ))
        csv_users = os.path.join(
            settings.BASE_DIR, 'data', 'users.csv'
        )
        try:
            with open(file=csv_users, mode='r', encoding='utf-8') as f:
                rows = csv.reader(f)
                for row in tqdm(
                    rows,
                    desc="Процесс загрузки тестовых пользователей:",
                    ncols=100,
                    unit=" users"
                ):
                    User.objects.get_or_create(
                        username=row[0],
                        password=row[1],
                        first_name=row[2],
                        last_name=row[3],
                        email=row[4]
                    )
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'Файл CSV не найден: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Что-то пошло не так: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                '=================== SUCCESS ==================='
            ))
        finally:
            self.stdout.write(self.style.SUCCESS(
                '################# FINISH LOAD #################'
            ))
