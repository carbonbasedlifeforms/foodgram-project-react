from django.conf import settings
from django.core.exceptions import ValidationError


def validate_count(value):
    """Метод проверки на значение меньше константы MIN_COUNT"""
    if not value or value < 1:
        raise ValidationError(
            f'Убедитесь, что это значение больше '
            f'либо равно {settings.MIN_COUNT}'
        )
    return value


def validate_cooking_time(value):
    """Метод валидации времени приготовления"""
    if value < settings.MIN_COOKING_TIME:
        raise ValidationError(
            f'Время приготовления должно быть '
            f'не меньше {settings.MIN_COOKING_TIME}'
        )
