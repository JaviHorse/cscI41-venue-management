from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView

from . import queries
from .forms import ReservationForm, VenueFilterForm
from .models import Customer
from .services import create_reservation, next_reservation_id


class VenueListView(LoginRequiredMixin, ListView):
    """/venues/ — all venues, narrowed by the filters in the URL query string."""
    template_name = 'venue-list.html'
    context_object_name = 'venues'

    def get_queryset(self):
        # Filters are read from request.GET, so a filtered list is just a URL that can be bookmarked.
        self.filter_form = VenueFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            f = self.filter_form.cleaned_data
            return queries.search_venues(
                building=f['building'],
                venue_type=f['type'],
                min_capacity=f['min_capacity'],
                amenity=f['amenity'],
                start=f['start'],
                end=f['end'],
            )
        return queries.search_venues()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        return context


class VenueDetailView(DetailView):
    """/venues/<venue_id>/ — one venue's details, plus the reservation form."""
    template_name = 'venue-detail.html'
    context_object_name = 'venue'
    # DetailView reads the ID from a URL parameter named "pk" by default, but our URL names it <venue_id>.
    # This tells it to read "venue_id" instead (it still matches against the model's primary key).
    pk_url_kwarg = 'venue_id'

    def get_queryset(self):
        return queries.venue_with_building()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amenities'] = queries.venue_amenities(self.object)
        context['assignment'] = queries.current_agent_assignment(self.object).first()
        context['renovations'] = queries.ongoing_renovations(self.object)

        if 'reservation_form' not in context:
            context['reservation_form'] = ReservationForm()

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        self.object = self.get_object()
        reservation_form = ReservationForm(request.POST)

        if reservation_form.is_valid():
            data = reservation_form.cleaned_data

            # The logged-in User links to a Customer through Profile; a Profile itself is not a Customer.
            customer = Customer.objects.filter(profile__user=request.user).first()
            if customer is None:
                reservation_form.add_error(None, 'Only customer accounts can make reservations.')
            elif data['start_datetime'] <= timezone.now():
                reservation_form.add_error('start_datetime', 'Start date/time must be in the future.')
            else:
                # create_reservation (services.py) already checks capacity, start < end,
                # overlapping reservations and renovations, so the view doesn't repeat them.
                try:
                    reservation = create_reservation(
                        reservation_id=next_reservation_id(),
                        venue_id=self.object.pk,
                        customer_id=customer.pk,
                        start_datetime=data['start_datetime'],
                        end_datetime=data['end_datetime'],
                        expected_participants=data['expected_participants'],
                    )
                    return redirect('core:reservation-detail', reservation_id=reservation.pk)
                except ValidationError as error:
                    for message in error.messages:
                        reservation_form.add_error(None, message)

        return self.render_to_response(
            self.get_context_data(reservation_form=reservation_form)
        )


class ReservationListView(LoginRequiredMixin, ListView):
    """/reservations/ — the logged-in customer's reservations."""
    template_name = 'reservation-list.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return queries.customer_reservations(self.request.user)


class ReservationDetailView(LoginRequiredMixin, DetailView):
    """/reservations/<reservation_id>/ — summary shown after booking."""
    template_name = 'reservation-detail.html'
    context_object_name = 'reservation'
    pk_url_kwarg = 'reservation_id'

    def get_queryset(self):
        # Limited to the user's own reservations, so other people's IDs give a 404.
        return queries.customer_reservations(self.request.user)
