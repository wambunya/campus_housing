from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['landlord', 'created_at', 'latitude', 'longitude']
        # You can add widgets here to style inputs with Tailwind classes if not using crispy-forms