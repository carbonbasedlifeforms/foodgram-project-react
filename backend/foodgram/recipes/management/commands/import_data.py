from csv import reader

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


IMPORT_OBJECTS = [
    (Ingredient, 'ingredients.csv'),
]


class Command(BaseCommand):

    help = 'Загрузка данных из файлов csv в таблицы бд через модели'

    def handle(self, *args, **options):

        for model, filename in IMPORT_OBJECTS:
            model_obj = model.objects.all()
            model_obj.delete()
            print(f'Загружаем {filename}...')
            with open(f'recipes/data/{filename}', 'r') as open_file:
                file_reader = reader(open_file)
                for row in file_reader:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
        print('Готово!')
