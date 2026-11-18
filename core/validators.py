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

# Reference: https://docs.djangoproject.com/en/6.0/ref/validators/#regexvalidator
def prefixed_id_validator(prefix):
    return RegexValidator(
        regex=rf'^{prefix}[0-9]{{4}}$',
        message=f'ID must be "{prefix}" followed by 4 digits, ex. {prefix}1001.'
    )