from django.contrib import admin
from .models import Stock, StockCount, StockCountItem


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['beverage', 'location', 'quantity', 'liters_display', 'last_updated', 'updated_by']
    list_filter = ['location', 'beverage__unit_type']
    search_fields = ['beverage__name', 'location__name']
    readonly_fields = ['last_updated']

    def liters_display(self, obj):
        return f"{obj.liters:.2f}L"
    liters_display.short_description = 'Liters'


class StockCountItemInline(admin.TabularInline):
    model = StockCountItem
    extra = 0
    readonly_fields = ['beverage', 'quantity', 'liters', 'unit_type_name', 'liters_per_unit']
    can_delete = False


@admin.register(StockCount)
class StockCountAdmin(admin.ModelAdmin):
    list_display = ['location', 'timestamp', 'counted_by', 'item_count', 'total_liters_display']
    list_filter = ['location', 'timestamp']
    search_fields = ['location__name', 'counted_by', 'notes']
    readonly_fields = ['timestamp']
    inlines = [StockCountItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    def total_liters_display(self, obj):
        return f"{obj.total_liters:.2f}L"
    total_liters_display.short_description = 'Total Liters'


@admin.register(StockCountItem)
class StockCountItemAdmin(admin.ModelAdmin):
    list_display = ['stock_count', 'beverage', 'quantity', 'liters', 'unit_type_name']
    list_filter = ['stock_count__location', 'stock_count__timestamp']
    search_fields = ['beverage__name', 'stock_count__location__name']
    readonly_fields = ['stock_count', 'beverage', 'quantity', 'liters', 'unit_type_name', 'liters_per_unit']
