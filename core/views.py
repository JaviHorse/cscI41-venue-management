from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView, ListView
from datetime import datetime
from django.utils import timezone
from .models import Venue, Reservation
from .forms import ReservationForm


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

        #TO DO: changed datetime fields to start_date, end_date, start_time, end_time in Reservation model
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

                    start_datetime_obj = datetime.combine(start_date_obj, start_time_obj)
                    end_datetime_obj = datetime.combine(end_date_obj, end_time_obj)

                    if start_datetime_obj >= end_datetime_obj:
                        context['datetime_error'] = (
                            'End date/time must be later than start date/time.'
                        )
                    else:
                        conflicting_reservations = Reservation.objects.filter(
                            venue__in=venues
                        ).exclude(
                            end_date__lt=start_date_obj
                        ).exclude(
                            end_date=start_date_obj,
                            end_time__lte=start_time_obj
                        ).exclude(
                            start_date__gt=end_date_obj
                        ).exclude(
                            start_date=end_date_obj,
                            start_time__gte=end_time_obj
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'reservation_form' not in context:
            context['reservation_form'] = ReservationForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        reservation_form = ReservationForm(request.POST)

        if not request.user.is_authenticated:
            return redirect('login')

        if reservation_form.is_valid():
            if reservation_form.cleaned_data['expected_participants'] > self.object.capacity:
                reservation_form.add_error(
                    'expected_participants', 'Not enough capacity available.'
                    )
                return self.render_to_response(
                    self.get_context_data(reservation_form=reservation_form)
                )
            if reservation_form.cleaned_data['start_datetime'] >= reservation_form.cleaned_data['end_datetime']:
                reservation_form.add_error(
                    'end_datetime', 'End date/time must be later than start date/time.'
                    )
                return self.render_to_response(
                    self.get_context_data(reservation_form=reservation_form)
                )
            if reservation_form.cleaned_data['start_datetime'] <= timezone.now():
                reservation_form.add_error(
                    'start_datetime', 'Start date/time must be in the future.'
                    )
                return self.render_to_response(
                    self.get_context_data(reservation_form=reservation_form)
                )
            #TO DO: change datetime fields to start_date, end_date, start_time, end_time in Reservation model
            start = reservation_form.cleaned_data['start_datetime']
            end = reservation_form.cleaned_data['end_datetime']

            if self.object.reservations.exclude(
                end_date__lt=start.date()
            ).exclude(
                end_date=start.date(),
                end_time__lte=start.time()
            ).exclude(
                start_date__gt=end.date()
            ).exclude(
                start_date=end.date(),
                start_time__gte=end.time()
            ).exists():
                reservation_form.add_error(
                    None, 'The venue is already reserved for the selected date and time.'
                    )
                return self.render_to_response(
                    self.get_context_data(reservation_form=reservation_form)
                )

            reservation = reservation_form.save(commit=False)

            reservation.customer = request.user.profile
            reservation.venue = self.object

            reservation.start_date = start.date()
            reservation.end_date = end.date()
            reservation.start_time = start.time()
            reservation.end_time = end.time()

            #need to generate a unique reservation_id

            reservation.save()
            return redirect('core:reservations')

        return self.render_to_response(
            self.get_context_data(reservation_form=reservation_form)
            )


class ReservationsListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations.html'

    def get_queryset(self):
        return Reservation.objects.filter(
            customer=self.request.user.profile
        ).select_related('venue')
