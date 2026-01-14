from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Stock, StockCount, StockCountItem


class StockResource(resources.ModelResource):
    class Meta:
        model = Stock
        fields = ('id', 'beverage', 'location', 'quantity', 'last_updated', 'updated_by')


class StockCountResource(resources.ModelResource):
    class Meta:
        model = StockCount
        fields = ('id', 'location', 'timestamp')


class StockCountItemResource(resources.ModelResource):
    class Meta:
        model = StockCountItem
        fields = ('id', 'stock_count', 'beverage', 'quantity', 'liters', 'unit_type_name', 'liters_per_unit')


@admin.register(Stock)
class StockAdmin(ImportExportModelAdmin):
    resource_class = StockResource
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
class StockCountAdmin(ImportExportModelAdmin):
    resource_class = StockCountResource
    list_display = ['location', 'timestamp', 'item_count', 'total_liters_display']
    list_filter = ['location', 'timestamp']
    search_fields = ['location__name']
    readonly_fields = ['timestamp']
    inlines = [StockCountItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    def total_liters_display(self, obj):
        return f"{obj.total_liters:.2f}L"
    total_liters_display.short_description = 'Total Liters'


@admin.register(StockCountItem)
class StockCountItemAdmin(ImportExportModelAdmin):
    resource_class = StockCountItemResource
    list_display = ['stock_count', 'beverage', 'quantity', 'liters', 'unit_type_name']
    list_filter = ['stock_count__location', 'stock_count__timestamp']
    search_fields = ['beverage__name', 'stock_count__location__name']
    readonly_fields = ['stock_count', 'beverage', 'quantity', 'liters', 'unit_type_name', 'liters_per_unit']
