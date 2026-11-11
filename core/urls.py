from django.urls import path
from .views import HomeView, VenueDetailView, ReservationsListView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('venue/<str:venue_id>/', VenueDetailView.as_view(), name='venue_detail'),
    path('reservations/', ReservationsListView.as_view(), name='reservations')
]
