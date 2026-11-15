from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView, ListView
from datetime import datetime
from django.utils import timezone
from .models import Venue, Reservation, Customer
from .forms import ReservationForm
from .services import create_reservation, next_reservation_id


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        venues = Venue.objects.all()

        building = self.request.GET.get('building')
        if building:
            venues = venues.filter(building__building_name__icontains=building)

        venue_type = self.request.GET.get('venue_type')
        if venue_type:
            venues = venues.filter(venue_type__icontains=venue_type)

        capacity = self.request.GET.get('capacity')
        if capacity:
            try:
                capacity = int(capacity)
                if capacity < 1:
                    raise ValueError
                venues = venues.filter(capacity__gte=capacity)
            except ValueError:
                context['capacity_error'] = 'Capacity must be a positive integer.'

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        start_time = self.request.GET.get('start_time')
        end_time = self.request.GET.get('end_time')

        if start_date or end_date or start_time or end_time:
            if not all([start_date, end_date, start_time, end_time]):
                context['datetime_error'] = 'Please provide both dates and both times.'
            else:
                try:
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

                    start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                    end_time_obj = datetime.strptime(end_time, '%H:%M').time()

                    # make_aware because USE_TZ=True stores aware datetimes in the DB.
                    start_datetime_obj = timezone.make_aware(datetime.combine(start_date_obj, start_time_obj))
                    end_datetime_obj = timezone.make_aware(datetime.combine(end_date_obj, end_time_obj))

                    if start_datetime_obj >= end_datetime_obj:
                        context['datetime_error'] = (
                            'End date/time must be later than start date/time.'
                        )
                    else:
                        # Two bookings overlap if one starts before the other ends (and vice versa).
                        # Using the model's datetime fields replaces the old split date/time excludes.
                        conflicting_reservations = Reservation.objects.filter(
                            venue__in=venues,
                            start_datetime__lt=end_datetime_obj,
                            end_datetime__gt=start_datetime_obj,
                        )

                        venues = venues.exclude(
                            pk__in=conflicting_reservations.values_list('venue_id', flat=True)
                        )

                except ValueError:
                    context['datetime_error'] = 'Please enter valid dates and times.'

        context['venues'] = venues
        return context


class VenueDetailView(DetailView):
    model = Venue
    template_name = 'venue-detail.html'
    # DetailView reads the ID from a URL parameter named "pk" by default, but our URL names it <venue_id>.
    # This tells it to read "venue_id" instead (it still matches against the model's primary key).
    pk_url_kwarg = 'venue_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
                    create_reservation(
                        reservation_id=next_reservation_id(),
                        venue_id=self.object.pk,
                        customer_id=customer.pk,
                        start_datetime=data['start_datetime'],
                        end_datetime=data['end_datetime'],
                        expected_participants=data['expected_participants'],
                    )
                    return redirect('core:reservations')
                except ValidationError as error:
                    for message in error.messages:
                        reservation_form.add_error(None, message)

        return self.render_to_response(
            self.get_context_data(reservation_form=reservation_form)
        )


class ReservationsListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations.html'

    def get_queryset(self):
        # Filter through Customer -> Profile -> User; returns nothing for non-customer accounts.
        return Reservation.objects.filter(
            customer__profile__user=self.request.user
        ).select_related('venue').order_by('start_datetime')
