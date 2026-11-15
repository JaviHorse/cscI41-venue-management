"""
Read-only (SELECT) queries used by the views.

Each function returns a Django ORM queryset. Keeping them here lets the views stay
thin and lets `python manage.py export_queries` print the exact SQL for the paper.
Writes (INSERT) go through services.py instead.
"""
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from .models import (
    AmenityType,
    Building,
    Renovation,
    Reservation,
    Venue,
    VenueAmenity,
    VenueAssignment,
)


# ---------- Filter dropdown options (venue list page) ----------

def building_options():
    return Building.objects.order_by('building_name')


def venue_type_options():
    return (
        Venue.objects
        .order_by('venue_type')
        .values_list('venue_type', flat=True)
        .distinct()
    )


def amenity_options():
    return AmenityType.objects.order_by('amenity_name')


# ---------- Venue list page: /venues/ ----------

def search_venues(building=None, venue_type=None, min_capacity=None,
                  amenity=None, start=None, end=None):
    """Venues matching the filters; any filter left as None is skipped."""
    venues = Venue.objects.select_related('building')

    if building:
        venues = venues.filter(building=building)
    if venue_type:
        venues = venues.filter(venue_type=venue_type)
    if min_capacity:
        venues = venues.filter(capacity__gte=min_capacity)
    if amenity:
        venues = venues.filter(venue_amenities__amenity=amenity)

    if start and end:
        # Two time ranges overlap when each one starts before the other ends.
        booked = Reservation.objects.filter(
            venue=OuterRef('pk'),
            start_datetime__lt=end,
            end_datetime__gt=start,
        )
        # Renovations are stored as dates, and an unfinished one has no Date_Completed yet.
        under_renovation = Renovation.objects.filter(
            venue=OuterRef('pk'),
            date_started__lte=timezone.localtime(end).date(),
        ).filter(
            Q(date_completed__isnull=True)
            | Q(date_completed__gte=timezone.localtime(start).date())
        )
        venues = venues.exclude(Exists(booked)).exclude(
            Exists(under_renovation))

    return venues.order_by('building__building_name', 'venue_name')


# ---------- Venue detail page: /venues/<venue_id>/ ----------

def venue_with_building():
    return Venue.objects.select_related('building')


def venue_amenities(venue):
    return (
        VenueAmenity.objects
        .filter(venue=venue)
        .select_related('amenity')
        .order_by('amenity__amenity_name')
    )


def current_agent_assignment(venue, today=None):
    """The agent handling the venue today; an assignment with no End_Date is still ongoing."""
    today = today or timezone.localdate()
    return (
        VenueAssignment.objects
        .filter(venue=venue, start_date__lte=today)
        .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
        .select_related('agent')
        .order_by('-start_date')
    )


def ongoing_renovations(venue, today=None):
    today = today or timezone.localdate()
    return (
        Renovation.objects
        .filter(venue=venue, date_started__lte=today)
        .filter(Q(date_completed__isnull=True) | Q(date_completed__gte=today))
    )


# ---------- Reservation pages: /reservations/ and /reservations/<reservation_id>/ ----------

def customer_reservations(user):
    # User -> Profile -> Customer; returns nothing for accounts that aren't customers.
    return (
        Reservation.objects
        .filter(customer__profile__user=user)
        .select_related('venue__building')
        .order_by('start_datetime')
    )
