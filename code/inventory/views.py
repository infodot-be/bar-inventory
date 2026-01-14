from django.shortcuts import render, redirect
from .models import Location


def not_logged_in(request):
    """Display a message when user is not logged in."""
    return render(request, 'inventory/not_logged_in.html')


def index(request):
    """Home page - select a location to manage inventory."""
    # If user is not authenticated, show not logged in page
    if not request.user.is_authenticated:
        return redirect('inventory:not_logged_in')

    # Staff members can see all locations
    if request.user.is_staff:
        locations = Location.objects.filter(is_active=True)
    # Regular users can only see their assigned location
    elif hasattr(request.user, 'location') and request.user.location:
        # Redirect directly to their location
        return redirect('stock:location_detail', location_id=request.user.location.id)
    else:
        locations = Location.objects.none()

    return render(request, 'inventory/index.html', {'locations': locations})
