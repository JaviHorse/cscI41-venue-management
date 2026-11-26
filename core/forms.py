from django import forms
from .models import Reservation, Renovation
from . import queries


class ReservationForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    end_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Reservation
        fields = ['expected_participants']


class VenueFilterForm(forms.Form):
    # Submitted with method="get", so the field names become the URL query string:
    # /venues/?building=...&type=...&min_capacity=...&amenities=...&amenities=...&start=...&end=...
    building = forms.ModelChoiceField(queryset=queries.building_options(), required=False)
    type = forms.ChoiceField(required=False)
    min_capacity = forms.IntegerField(min_value=1, required=False)
    # Checkboxes, so a customer can tick several amenities; a venue must have all of them.
    amenities = forms.ModelMultipleChoiceField(
        queryset=queries.amenity_options(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    start = forms.DateTimeField(
        required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    end = forms.DateTimeField(
        required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Built per request so newly added venue types show up without a restart.
        self.fields['type'].choices = [('', 'Any type')] + [
            (t, t) for t in queries.venue_type_options()
        ]

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get('start'), cleaned.get('end')
        if bool(start) != bool(end):
            raise forms.ValidationError('Please provide both a start and an end date/time.')
        if start and end and start >= end:
            raise forms.ValidationError('End date/time must be later than start date/time.')
        return cleaned


class RenovationForm(forms.ModelForm):
    class Meta:
        model = Renovation
        fields = ['remarks']
        