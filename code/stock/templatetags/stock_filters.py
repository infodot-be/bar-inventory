from django import template
import math

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Template filter to get dictionary item by key."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def floor_decimal(value, decimal_places=2):
    """Floor a decimal value to specified decimal places."""
    if value is None:
        return None
    try:
        multiplier = 10 ** decimal_places
        return math.floor(float(value) * multiplier) / multiplier
    except (ValueError, TypeError):
        return value
