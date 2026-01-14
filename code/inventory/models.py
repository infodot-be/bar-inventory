from django.db import models
from django.contrib.auth.models import User
import random


# Predefined list of nice, distinct colors for beverages
BEVERAGE_COLORS = [
    'rgb(75, 192, 192)',   # Teal
    'rgb(255, 159, 64)',   # Orange
    'rgb(153, 102, 255)',  # Purple
    'rgb(255, 206, 86)',   # Yellow
    'rgb(231, 76, 60)',    # Dark Red
    'rgb(46, 204, 113)',   # Green
    'rgb(155, 89, 182)',   # Violet
    'rgb(52, 152, 219)',   # Light Blue
    'rgb(241, 196, 15)',   # Gold
    'rgb(230, 126, 34)',   # Carrot
    'rgb(26, 188, 156)',   # Turquoise
    'rgb(149, 165, 166)',  # Gray
    'rgb(236, 112, 99)',   # Pink
    'rgb(142, 68, 173)',   # Deep Purple
    'rgb(39, 174, 96)',    # Emerald
    'rgb(243, 156, 18)',   # Bright Orange
    'rgb(192, 57, 43)',    # Crimson
    'rgb(22, 160, 133)',   # Dark Turquoise
    'rgb(211, 84, 0)',     # Burnt Orange
    'rgb(41, 128, 185)',   # Ocean Blue
]


def get_random_color():
    """Get a random color from the predefined list."""
    return random.choice(BEVERAGE_COLORS)


class Location(models.Model):
    """Represents a location in the bar where beverages are stored."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='location',
        help_text="User assigned to this location (can only view this location)"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UnitType(models.Model):
    """Represents the unit type for measuring beverages."""
    name = models.CharField(max_length=100, help_text="Unit type name (e.g., Tray, Barrel, Bottle)")
    quantity = models.IntegerField(
        default=1,
        help_text="Number of items per unit (e.g., 6 bottles per tray, 12 bottles per tray)"
    )

    class Meta:
        ordering = ['name', 'quantity']
        unique_together = ['name', 'quantity']

    def __str__(self):
        # Extract base name (e.g., "TRAY_6" -> "TRAY")
        base_name = self.name.split('_')[0] if '_' in self.name else self.name
        if self.quantity > 1:
            return f"{base_name} ({self.quantity})"
        return base_name


class Beverage(models.Model):
    """Represents a beverage that can be stocked."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    liters_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        help_text="How many liters per unit for this specific beverage"
    )
    alarm_minimum = models.IntegerField(
        default=1,
        help_text="Minimum quantity threshold for low stock alert"
    )
    color = models.CharField(
        max_length=20,
        default=get_random_color,
        help_text="Color for chart display (e.g., 'rgb(255, 99, 132)' or '#ff6384')"
    )
    is_active = models.BooleanField(default=True)
    available_locations = models.ManyToManyField(
        Location,
        related_name='beverages',
        help_text="Locations where this beverage is available"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit_type}, {self.liters_per_unit}L)"
