from django.core.exceptions import ValidationError
from django.utils import timezone


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
