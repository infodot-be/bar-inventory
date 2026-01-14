"""Utility functions for stock management."""
from decimal import Decimal
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from inventory.models import Location, Beverage


def get_location_stock_summary(location):
    """
    Calculate stock summary for a location.

    Args:
        location: Location object

    Returns:
        dict: Summary with item_count and total_liters
    """
    from .models import Stock

    stocks = Stock.objects.filter(location=location, beverage__is_active=True)
    item_count = stocks.count()
    total_liters = sum(stock.liters for stock in stocks)

    return {
        'location': location,
        'item_count': item_count,
        'total_liters': total_liters
    }


def prepare_chart_data_for_location(location, recent_counts):
    """
    Prepare chart data for beverages at a location.

    Args:
        location: Location object
        recent_counts: QuerySet of StockCount objects

    Returns:
        dict: Chart data organized by beverage ID
    """
    if not recent_counts:
        return None

    all_beverages = Beverage.objects.filter(
        is_active=True,
        available_locations=location
    ).order_by(Lower('name'))

    chart_data = {}
    for beverage in all_beverages:
        beverage_data = {
            'labels': [],
            'data': [],
            'alarm_minimum': beverage.alarm_minimum,
            'color': beverage.color,
            'liters_per_unit': float(beverage.liters_per_unit)
        }
        # Reverse to get chronological order (oldest to newest)
        for count in reversed(list(recent_counts)):
            count_items = {item.beverage.id: float(item.quantity) for item in count.items.all()}
            # Use ISO format with timezone to avoid timezone issues in JavaScript
            beverage_data['labels'].append(count.timestamp.isoformat())
            beverage_data['data'].append(count_items.get(beverage.id, 0))

        chart_data[beverage.id] = beverage_data

    return chart_data


def get_or_create_stock_for_location(location):
    """
    Get or create stock entries for all beverages at a location.

    Args:
        location: Location object

    Returns:
        list: List of dicts with beverage, stock, and liters info (sorted alphabetically by beverage name)
    """
    from .models import Stock

    beverages = location.beverages.filter(is_active=True).order_by(Lower('name'))
    stock_data = []

    for beverage in beverages:
        stock, created = Stock.objects.get_or_create(
            beverage=beverage,
            location=location,
            defaults={'quantity': 0}
        )
        stock_data.append({
            'beverage': beverage,
            'stock': stock,
            'liters': stock.liters
        })

    return stock_data


def update_stock_quantity(stock, quantity, updated_by='User'):
    """
    Update stock quantity.

    Args:
        stock: Stock object
        quantity: New quantity value
        updated_by: User who made the update

    Returns:
        Stock: Updated stock object
    """
    stock.quantity = Decimal(str(quantity))
    stock.updated_by = updated_by
    stock.save()
    return stock


def adjust_stock_quantity(stock, adjustment, updated_by='User'):
    """
    Adjust stock quantity by a relative amount.

    Args:
        stock: Stock object
        adjustment: Amount to adjust (positive or negative)
        updated_by: User who made the adjustment

    Returns:
        Stock: Updated stock object
    """
    adjustment_decimal = Decimal(str(adjustment))
    stock.quantity = max(Decimal('0'), stock.quantity + adjustment_decimal)
    stock.updated_by = updated_by
    stock.save()
    return stock


def create_stock_count(location, stocks):
    """
    Create a stock count record with all items.

    Args:
        location: Location object
        stocks: QuerySet of Stock objects to count

    Returns:
        StockCount: Created stock count object
    """
    from .models import StockCount, StockCountItem

    stock_count = StockCount.objects.create(
        location=location
    )

    for stock in stocks:
        StockCountItem.objects.create(
            stock_count=stock_count,
            beverage=stock.beverage,
            quantity=stock.quantity,
            liters=Decimal(str(stock.liters)),
            unit_type_name=str(stock.beverage.unit_type),
            liters_per_unit=stock.beverage.liters_per_unit
        )

    return stock_count
