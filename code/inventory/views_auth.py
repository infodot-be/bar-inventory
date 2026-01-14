"""Authentication views for location users."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.views.decorators.http import require_http_methods
import logging
from .tokens import location_token_generator
from .models import Location

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def token_login(request, uidb64, token):
    """Login a user using a token link.

    Security considerations:
    - Tokens expire after PASSWORD_RESET_TIMEOUT (default 1 hour)
    - Tokens are invalidated if user is deactivated or password changes
    - Failed attempts are logged for monitoring
    - Users are redirected to their assigned location only
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.warning(f"Token login failed: Invalid user ID in token. Error: {e}")
        user = None

    if user is not None and user.is_active and location_token_generator.check_token(user, token):
        login(request, user)
        logger.info(f"User {user.username} logged in via token")
        # Redirect to their location if they have one
        if hasattr(user, 'location') and user.location:
            return redirect('stock:location_detail', location_id=user.location.id)
        return redirect('inventory:index')
    else:
        logger.warning(f"Token login failed: Invalid or expired token for uidb64={uidb64}")
        return render(request, 'inventory/token_invalid.html', {
            'error': 'The login link is invalid or has expired.'
        })


@require_http_methods(["GET"])
def generate_token_link(request, location_id):
    """Generate a token link for a location user (staff only).

    Security notes:
    - Only staff members can generate token links
    - Tokens are time-limited and single-purpose
    - Each token generation is logged
    - Inactive users cannot receive tokens
    """
    if not request.user.is_authenticated:
        return redirect('inventory:not_logged_in')

    if not request.user.is_staff:
        logger.warning(f"Non-staff user {request.user.username} attempted to generate token for location {location_id}")
        return redirect('inventory:index')

    location = get_object_or_404(Location, id=location_id)

    if not location.user:
        return render(request, 'inventory/generate_token.html', {
            'error': 'This location does not have an assigned user.',
            'location': location
        })

    if not location.user.is_active:
        return render(request, 'inventory/generate_token.html', {
            'error': 'The assigned user account is inactive.',
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

    logger.info(f"Staff user {request.user.username} generated token for location {location.name} (user: {location.user.username})")

    return render(request, 'inventory/generate_token.html', {
        'location': location,
        'token_url': token_url
    })
