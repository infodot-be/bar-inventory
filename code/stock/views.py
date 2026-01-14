from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Sum, F, DecimalField
from inventory.models import Location, Beverage
from .models import Stock, StockCount, StockCountItem
from decimal import Decimal
import json


def stock_overview(request, location_id=None):
    """Show overview of stock for a specific location or all locations."""
    if location_id:
        selected_location = get_object_or_404(Location, id=location_id, is_active=True)
        locations = [selected_location]
    else:
        selected_location = None
        locations = Location.objects.filter(is_active=True)

    # Get stock summary by location
    location_summaries = []
    total_items = 0
    total_liters = 0

    for location in locations:
        stocks = Stock.objects.filter(location=location, beverage__is_active=True)
        item_count = stocks.count()
        location_liters = sum(stock.liters for stock in stocks)

        location_summaries.append({
            'location': location,
            'item_count': item_count,
            'total_liters': location_liters
        })

        total_items += item_count
        total_liters += location_liters

    # Get recent stock counts, filtered by location if specified
    if location_id:
        recent_counts = StockCount.objects.filter(location_id=location_id).order_by('-timestamp')[:30]
    else:
        recent_counts = StockCount.objects.all().order_by('-timestamp')[:10]

    # Get all beverages for table columns (or charts if location selected)
    if location_id:
        # For location view, only show beverages available at that location
        all_beverages = Beverage.objects.filter(
            is_active=True,
            available_locations=selected_location
        ).order_by('name')
    else:
        all_beverages = Beverage.objects.filter(is_active=True).order_by('name')

    # Prepare count data with beverage quantities
    count_data = []
    for count in recent_counts:
        count_items = {item.beverage.id: item.quantity for item in count.items.all()}
        count_data.append({
            'count': count,
            'beverages': {beverage.id: count_items.get(beverage.id, 0) for beverage in all_beverages}
        })

    # Prepare chart data for location view (time series for each beverage)
    chart_data = None
    if location_id and recent_counts:
        chart_data = {}
        for beverage in all_beverages:
            beverage_data = {
                'labels': [],
                'data': [],
                'alarm_minimum': beverage.alarm_minimum,
                'color': beverage.color
            }
            # Reverse to get chronological order (oldest to newest)
            for count in reversed(list(recent_counts)):
                count_items = {item.beverage.id: float(item.quantity) for item in count.items.all()}
                # Use ISO format with timezone to avoid timezone issues in JavaScript
                beverage_data['labels'].append(count.timestamp.isoformat())
                beverage_data['data'].append(count_items.get(beverage.id, 0))

            chart_data[beverage.id] = beverage_data

    # Convert chart_data to JSON for JavaScript
    chart_data_json = json.dumps(chart_data) if chart_data else None

    context = {
        'selected_location': selected_location,
        'location_summaries': location_summaries,
        'total_items': total_items,
        'total_liters': total_liters,
        'all_beverages': all_beverages,
        'count_data': count_data,
        'chart_data': chart_data_json,
    }

    return render(request, 'stock/overview.html', context)


def location_detail(request, location_id):
    """Show all beverages for a specific location with current stock."""
    location = get_object_or_404(Location, id=location_id, is_active=True)

    # Get all beverages available at this location
    beverages = location.beverages.filter(is_active=True)

    # Get or create stock entries for each beverage
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

    context = {
        'location': location,
        'stock_data': stock_data,
    }

    return render(request, 'inventory/location_detail.html', context)


@require_http_methods(["POST"])
def update_stock(request, stock_id):
    """Update stock quantity via HTMX."""
    stock = get_object_or_404(Stock, id=stock_id)

    try:
        new_quantity = request.POST.get('quantity', '0')
        stock.quantity = Decimal(new_quantity)
        stock.updated_by = request.POST.get('updated_by', 'User')
        stock.save()

        # Return updated HTML fragment for HTMX
        context = {
            'beverage': stock.beverage,
            'stock': stock,
            'liters': stock.liters
        }
        return render(request, 'inventory/partials/stock_row.html', context)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def quick_adjust(request, stock_id):
    """Quick adjust stock (increment/decrement) via HTMX."""
    stock = get_object_or_404(Stock, id=stock_id)

    try:
        adjustment = Decimal(request.POST.get('adjustment', '0'))
        stock.quantity = max(Decimal('0'), stock.quantity + adjustment)
        stock.updated_by = request.POST.get('updated_by', 'User')
        stock.save()

        # Return updated HTML fragment for HTMX
        context = {
            'beverage': stock.beverage,
            'stock': stock,
            'liters': stock.liters
        }
        return render(request, 'inventory/partials/stock_row.html', context)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def save_count(request, location_id):
    """Save current stock count for a location."""
    location = get_object_or_404(Location, id=location_id, is_active=True)

    try:
        # Create the stock count record
        stock_count = StockCount.objects.create(
            location=location,
            counted_by=request.POST.get('counted_by', 'User'),
            notes=request.POST.get('notes', '')
        )

        # Get all current stock for this location
        stocks = Stock.objects.filter(location=location, beverage__is_active=True)

        # Create count items for each stock entry
        for stock in stocks:
            StockCountItem.objects.create(
                stock_count=stock_count,
                beverage=stock.beverage,
                quantity=stock.quantity,
                liters=Decimal(str(stock.liters)),
                unit_type_name=str(stock.beverage.unit_type),
                liters_per_unit=stock.beverage.liters_per_unit
            )

        messages.success(request, f'Stock count saved successfully! {stocks.count()} items recorded.')
        return redirect('stock:location_detail', location_id=location_id)
    except Exception as e:
        messages.error(request, f'Error saving count: {str(e)}')
        return redirect('stock:location_detail', location_id=location_id)
