from django.db import models
from inventory.models import Location, Beverage


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
        """Calculate the total liters based on quantity, unit type quantity, and beverage's liters per unit."""
        return float(self.quantity) * float(self.beverage.unit_type.quantity) * float(self.beverage.liters_per_unit)

    def __str__(self):
        return f"{self.beverage.name} at {self.location.name}: {self.quantity} units ({self.liters:.2f}L)"


class StockCount(models.Model):
    """Represents a saved count/snapshot of inventory at a location."""
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='counts')
    timestamp = models.DateTimeField(auto_now_add=True)
    counted_by = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.location.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @property
    def total_liters(self):
        """Calculate total liters in this count."""
        return sum(item.liters for item in self.items.all())


class StockCountItem(models.Model):
    """Individual beverage quantities in a stock count."""
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name='items')
    beverage = models.ForeignKey(Beverage, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Number of units at time of count"
    )
    liters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total liters at time of count"
    )
    unit_type_name = models.CharField(max_length=50)
    liters_per_unit = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        ordering = ['beverage__name']

    def __str__(self):
        return f"{self.beverage.name}: {self.quantity} units ({self.liters}L)"
