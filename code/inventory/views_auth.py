"""Authentication views for location users."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .tokens import location_token_generator
from .models import Location


def token_login(request, uidb64, token):
    """Login a user using a token link."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and location_token_generator.check_token(user, token):
        login(request, user)
        # Redirect to their location if they have one
        if hasattr(user, 'location') and user.location:
            return redirect('stock:location_detail', location_id=user.location.id)
        return redirect('inventory:index')
    else:
        return render(request, 'inventory/token_invalid.html', {
            'error': 'The login link is invalid or has expired.'
        })


def generate_token_link(request, location_id):
    """Generate a token link for a location user (staff only)."""
    if not request.user.is_staff:
        return redirect('inventory:index')

    location = get_object_or_404(Location, id=location_id)

    if not location.user:
        return render(request, 'inventory/generate_token.html', {
            'error': 'This location does not have an assigned user.',
            'location': location
        })

    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    uidb64 = urlsafe_base64_encode(force_bytes(location.user.pk))
    token = location_token_generator.make_token(location.user)

    # Build the full URL
    token_url = request.build_absolute_uri(
        f'/token-login/{uidb64}/{token}/'
    )

    return render(request, 'inventory/generate_token.html', {
        'location': location,
        'token_url': token_url
    })
