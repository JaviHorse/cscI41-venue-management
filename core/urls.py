from django.urls import path
from django.views.generic import RedirectView

from .views import (
    AgentVenueListView,
    AgentVenueDetailView,
    ReservationDetailView,
    ReservationListView,
    VenueDetailView,
    VenueListView,
)

app_name = 'core'

# URL conventions:
# - lowercase plural nouns; the path identifies one record (/venues/<venue_id>/)
# - filters go in the query string (/venues/?type=...&min_capacity=...)
# - route names are "<noun>-list" / "<noun>-detail", used as {% url 'core:venue-detail' venue.pk %}
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='core:venue-list'), name='home'),
    path('agent/venues/', AgentVenueListView.as_view(), name='agent-venue-list'),
    path('agent/venues/<str:venue_id>/', AgentVenueDetailView.as_view(), name='agent-venue-detail'),
    path('venues/', VenueListView.as_view(), name='venue-list'),
    path('venues/<str:venue_id>/', VenueDetailView.as_view(), name='venue-detail'),
    path('reservations/', ReservationListView.as_view(), name='reservation-list'),
    path('reservations/<str:reservation_id>/', ReservationDetailView.as_view(), name='reservation-detail'),
]
