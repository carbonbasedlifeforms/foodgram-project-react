from django.core.exceptions import ValidationError


def validate_count(value):
    if not value or value < 1:
        raise ValidationError(
            'Убедитесь, что это значение больше либо равно 1'
        )
    return value
