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
    BARREL = 'BARREL'
    TRAY = 'TRAY'
    BOTTLE = 'BOTTLE'

    UNIT_CHOICES = [
        (BARREL, 'Barrel'),
        (TRAY, 'Tray'),
        (BOTTLE, 'Bottle'),
    ]

    name = models.CharField(max_length=20, choices=UNIT_CHOICES, unique=True)
    liters_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="How many liters per unit (e.g., 50 liters per barrel)"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.get_name_display()} ({self.liters_per_unit}L)"


class Beverage(models.Model):
    """Represents a beverage that can be stocked."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    available_locations = models.ManyToManyField(
        Location,
        related_name='beverages',
        help_text="Locations where this beverage is available"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit_type.get_name_display()})"


class Stock(models.Model):
    """Represents the current stock of a beverage at a specific location."""
    beverage = models.ForeignKey(Beverage, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Number of units (barrels, trays, or bottles)"
    )
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['location', 'beverage']
        unique_together = ['beverage', 'location']

    @property
    def liters(self):
        """Calculate the total liters based on quantity and unit type."""
        return float(self.quantity) * float(self.beverage.unit_type.liters_per_unit)

    def __str__(self):
        return f"{self.beverage.name} at {self.location.name}: {self.quantity} units ({self.liters:.2f}L)"
