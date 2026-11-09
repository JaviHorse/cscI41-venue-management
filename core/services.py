
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
    reservation_id,
    venue_id,
    customer_id,
    start_datetime,
    end_datetime,
    expected_participants,
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
    renovation_id,
    venue_id,
    date_started,
    date_completed=None,
    remarks=None,
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