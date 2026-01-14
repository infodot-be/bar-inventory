from django.contrib import admin
from django.utils.html import format_html
from .models import Location, UnitType, Beverage


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
    list_display = ['name', 'quantity']
    ordering = ['name', 'quantity']


@admin.register(Beverage)
class BeverageAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'unit_type', 'liters_per_unit', 'is_active', 'location_count']
    list_filter = ['is_active', 'unit_type']
    search_fields = ['name', 'description']
    filter_horizontal = ['available_locations']

    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background-color: {}; border-radius: 50%; border: 1px solid #ccc;"></span>',
            obj.color
        )
    color_display.short_description = 'Color'

    def location_count(self, obj):
        return obj.available_locations.count()
    location_count.short_description = 'Locations'
