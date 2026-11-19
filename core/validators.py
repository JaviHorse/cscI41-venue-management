from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator

def validate_not_future(value):
    if value > timezone.localdate():
        raise ValidationError(
            "Date cannot be later than the current date."
        )


def validate_past_date(value):
    if value >= timezone.localdate():
        raise ValidationError(
            "Date must be earlier than the current date."
        )


# Every primary key is a system-generated 7-digit code, ex. 1000001
# Reference: https://docs.djangoproject.com/en/6.0/ref/validators/#regexvalidator
seven_digit_id_validator = RegexValidator(
    regex=r'^[0-9]{7}$',
    message='ID must be exactly 7 digits, ex. 1000001'
)