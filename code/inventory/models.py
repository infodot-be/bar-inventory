from django.db import models


class Location(models.Model):
    """Represents a location in the bar where beverages are stored."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

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
        default='rgb(54, 162, 235)',
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
