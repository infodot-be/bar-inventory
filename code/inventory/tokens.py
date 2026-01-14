"""Token-based authentication for location users."""
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class LocationTokenGenerator(PasswordResetTokenGenerator):
    """Generate tokens for location users to access their specific location.

    Tokens are time-based and expire after a certain period (default Django setting).
    By default, tokens expire after PASSWORD_RESET_TIMEOUT seconds (3600 = 1 hour in Django 3.1+).
    """

    def _make_hash_value(self, user, timestamp):
        """Include user's pk, timestamp, and active status in the hash.

        This ensures tokens become invalid if:
        - User is deactivated
        - Password is changed
        - Sufficient time has passed
        """
        return f"{user.pk}{timestamp}{user.is_active}"


location_token_generator = LocationTokenGenerator()
