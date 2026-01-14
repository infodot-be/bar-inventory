from django.contrib import admin
from .models import Location, UnitType, Beverage, Stock


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'beverage_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

    def beverage_count(self, obj):
        return obj.beverages.count()
    beverage_count.short_description = 'Beverages'


@admin.register(UnitType)
class UnitTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'liters_per_unit']
    ordering = ['name']


@admin.register(Beverage)
class BeverageAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit_type', 'is_active', 'location_count']
    list_filter = ['is_active', 'unit_type']
    search_fields = ['name', 'description']
    filter_horizontal = ['available_locations']

    def location_count(self, obj):
        return obj.available_locations.count()
    location_count.short_description = 'Locations'


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['beverage', 'location', 'quantity', 'liters_display', 'last_updated', 'updated_by']
    list_filter = ['location', 'beverage__unit_type']
    search_fields = ['beverage__name', 'location__name']
    readonly_fields = ['last_updated']

    def liters_display(self, obj):
        return f"{obj.liters:.2f}L"
    liters_display.short_description = 'Liters'
