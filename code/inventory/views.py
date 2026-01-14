from django.shortcuts import render
from .models import Location


def index(request):
    """Home page - select a location to manage inventory."""
    locations = Location.objects.filter(is_active=True)
    return render(request, 'inventory/index.html', {'locations': locations})
