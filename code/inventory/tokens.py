"""Token-based authentication for location users."""
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class LocationTokenGenerator(PasswordResetTokenGenerator):
    """Generate tokens for location users to access their specific location."""

    def _make_hash_value(self, user, timestamp):
        """Include user's pk and timestamp in the hash."""
        return f"{user.pk}{timestamp}{user.is_active}"


location_token_generator = LocationTokenGenerator()
