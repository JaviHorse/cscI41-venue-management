from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.urls import reverse


from . import queries
from .forms import ReservationForm, VenueFilterForm, RenovationForm, VenueAmenityForm
from .models import Customer
from .services import create_reservation, create_renovation, complete_renovation, create_venue_amenity


class AgentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    # Reference: https://docs.djangoproject.com/en/6.1/topics/auth/default/#django.contrib.auth.mixins.UserPassesTestMixin
    # Basically lets us write our own function that decides whether a user
    # can access our page or not. Hence, the below

    def test_func(self):
        """
        True = user has Agent profile. Let them through.
        False = user has no Agent profile. Do not let them through.
        """
        self.agent = queries.agent_for_user(self.request.user)
        return self.agent is not None

class AgentVenueListView(AgentRequiredMixin, ListView):
    """
    /agent/venues/
    Here we display the venues that the agent is currently handling.
    """
    template_name = 'agent-venue-list.html'
    context_object_name = 'venues'

    def get_queryset(self):
        return queries.agent_venues(self.request.user)

class AgentVenueDetailView(AgentRequiredMixin, DetailView):
    """
    /agent/venues/<venue_id>/
    Detail page of a venue that an agent manages.
    Shows its reservations, renovation status, and amenities.
    """
    template_name = 'agent-venue-detail.html'
    context_object_name = 'venue'
    pk_url_kwarg = 'venue_id'

    def get_queryset(self):
        return queries.agent_venues(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_reservations'] = queries.upcoming_venue_reservations(self.object)
        context['past_reservations'] = queries.past_venue_reservations(self.object)
        context['renovation'] = queries.ongoing_renovations(self.object).first()
        context['amenities'] = queries.venue_amenities(self.object)
        if 'renovation_form' not in context:
            context['renovation_form'] = RenovationForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        renovation_form = RenovationForm()
        action = request.POST.get('action')

        if action == 'start_renovation':
            renovation_form = RenovationForm(request.POST)
            if renovation_form.is_valid():
                try:
                    create_renovation(
                        venue_id=self.object.pk,
                        date_started=timezone.localdate(),
                        remarks=renovation_form.cleaned_data['remarks'] or None,
                    )
                    return redirect('core:agent-venue-detail', venue_id=self.object.pk)
                except ValidationError as error:
                    for message in error.messages:
                        renovation_form.add_error(None, message)

        elif action == 'complete_renovation':
            renovation_form = RenovationForm(request.POST)
            renovation = queries.ongoing_renovations(self.object).first()
            if renovation is None:
                renovation_form.add_error(None, 'This venue is not under renovation.')
            else: 
                try: 
                    complete_renovation(renovation.pk)
                    return redirect('core:agent-venue-detail', venue_id=self.object.pk)
                except ValidationError as error:
                    for message in error.messages:
                        renovation_form.add_error(None, message)
        return self.render_to_response(self.get_context_data(renovation_form=renovation_form))

class AgentVenueAmenityCreateView(AgentRequiredMixin, CreateView):
    """
    /agent/venues/<venue_id>/amenities/new/
    Adds an amenity to a venue that the agent manages.
    """
    form_class = VenueAmenityForm
    template_name = 'agent-venue-amenity-form.html' # TODO: make this template

    def get_venue(self):
        # Make sure the venue is assigned to the agent
        return get_object_or_404(queries.agent_venues(self.request.user), pk=self.kwargs['venue_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venue'] = self.get_venue()
        return context

    def form_valid(self, form):
        venue = self.get_venue()
        try:
            create_venue_amenity(venue_id=venue.pk, **form.cleaned_data)
        except ValidationError as error:
            for message in error.messages:
                form.add_error(None, message)
            return self.form_invalid(form)
        return redirect('core:agent-venue-detail', venue_id=venue.pk)

class AgentVenueAmenityUpdateView(AgentRequiredMixin, UpdateView):
    """
    /agent/venue-amenities/<venue_amenity_id>/edit/
    Edits an amenity on a venue the agent manages.
    """
    form_class = VenueAmenityForm
    template_name = 'agent-venue-amenity-form.html'
    context_object_name = 'venue_amenity'
    pk_url_kwarg = 'venue_amenity_id'

    def get_queryset(self):
        return queries.agent_venue_amenities(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venue'] = self.object.venue
        return context

    def get_success_url(self):
        return reverse('core:agent-venue-detail', kwargs={'venue_id': self.object.venue_id})




class VenueListView(ListView):
    """/venues/ — all venues, narrowed by the filters in the URL query string.

    Public: anyone can browse venues. Logging in is only needed to reserve
    (see VenueDetailView.post) and to see your own reservations.
    """
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
                amenities=f['amenities'],
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
