
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from core.models import (
    Venue,
    Reservation,
    Renovation,
)


def _local_date(value):
    if timezone.is_aware(value):
        return timezone.localtime(value).date()
    return value.date()


def _reservation_overlaps_renovation(reservation, renovation):
    start_date = _local_date(reservation.start_datetime)
    end_date = _local_date(reservation.end_datetime)

    return (
        end_date >= renovation.date_started
        and (
            renovation.date_completed is None
            or start_date <= renovation.date_completed
        )
    )


@transaction.atomic
def create_reservation(
    venue_id,
    customer_id,
    start_datetime,
    end_datetime,
    expected_participants,
    reservation_id=None,
):
    venue = Venue.objects.get(pk=venue_id)

    if start_datetime >= end_datetime:
        raise ValidationError(
            "Reservation end time must be after start time."
        )

    if expected_participants < 1:
        raise ValidationError(
            "Expected participants must be at least 1."
        )

    if expected_participants > venue.capacity:
        raise ValidationError(
            "Expected participants exceed venue capacity."
        )

    overlapping = Reservation.objects.filter(
        venue_id=venue_id,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    )

    if overlapping.exists():
        raise ValidationError(
            "This venue is already reserved during that period."
        )

    # Generate a new reservation id if none was provided
    if reservation_id is None:
        reservation_id = next_id(Reservation)
    
    candidate = Reservation(
        reservation_id=reservation_id,
        venue_id=venue_id,
        customer_id=customer_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        expected_participants=expected_participants,
    )

    renovations = Renovation.objects.filter(
        venue_id=venue_id
    )

    for renovation in renovations:
        if _reservation_overlaps_renovation(
            candidate, renovation
        ):
            raise ValidationError(
                "This venue is undergoing renovation "
                "during the selected period."
            )

    candidate.full_clean()
    candidate.save()

    return candidate


@transaction.atomic
def create_renovation(
    venue_id,
    date_started,
    date_completed=None,
    remarks=None,
    renovation_id=None
):
    if date_completed is not None:
        if date_completed < date_started:
            raise ValidationError(
                "Renovation completion cannot precede its start."
            )

    overlapping = Renovation.objects.filter(
        venue_id=venue_id
    )

    if date_completed is None:
        overlapping = overlapping.filter(
            models.Q(date_completed__isnull=True)
            | models.Q(date_completed__gte=date_started)
        )
    else:
        overlapping = overlapping.filter(
            date_started__lte=date_completed
        ).filter(
            models.Q(date_completed__isnull=True)
            | models.Q(date_completed__gte=date_started)
        )

    if overlapping.exists():
        raise ValidationError(
            "This venue has an overlapping renovation."
        )

    # Generate a new renovation id if none is provided
    if renovation_id is None:
        renovation_id = next_id(Renovation)

    candidate = Renovation(
        renovation_id=renovation_id,
        venue_id=venue_id,
        date_started=date_started,
        date_completed=date_completed,
        remarks=remarks,
    )

    reservations = Reservation.objects.filter(
        venue_id=venue_id
    )

    for reservation in reservations:
        if _reservation_overlaps_renovation(
            reservation, candidate
        ):
            raise ValidationError(
                "An existing reservation conflicts "
                "with this renovation."
            )

    candidate.full_clean()
    candidate.save()

    return candidate

@transaction.atomic
def complete_renovation(renovation_id, date_completed=None):
    """
    Marks an ongoing renovation as done. date_completed is default today.
    date_complted is the renovation's last day. The venue will reopen after it.
    """
    renovation = Renovation.objects.get(pk=renovation_id)
    date_completed = date_completed or timezone.localdate()

    if renovation.date_completed is not None:
        raise ValidationError("This renovation is already completed.")

    if date_completed < renovation.date_started:
        raise ValidationError("Renovation completion cannot precede start date.")

    renovation.date_completed = date_completed
    renovation.full_clean()
    renovation.save()

    return renovation

def next_id(model):
    """
    Return the next 7-digit ID for the table, ex. 1000005 -> 1000006.
    Empty tables start at 1000001.
    Use this whenever we make a new record. Do not type IDs manually.
    """
    last = model.objects.aggregate(last=models.Max('pk'))['last']
    number = int(last) + 1 if last else 1000001
    if number > 9999999:
        raise ValidationError(
            # Reference: https://stackoverflow.com/questions/44602786/how-to-get-table-name-from-django-filter-objects
            f"No 7-digit IDs left for {model._meta.db_table}."
        )
    return f"{number:07d}"
    
    

