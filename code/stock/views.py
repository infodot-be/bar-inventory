from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models.functions import Lower
from django.utils import timezone
from inventory.models import Location, Beverage
from .models import Stock, StockCount
from .utils import (
    get_location_stock_summary,
    prepare_chart_data_for_location,
    get_or_create_stock_for_location,
    update_stock_quantity,
    adjust_stock_quantity,
    create_stock_count
)
import json


def stock_overview(request, location_id=None):
    """Show overview of stock for a specific location or all locations."""
    # Check authentication
    if not request.user.is_authenticated:
        return redirect('inventory:not_logged_in')

    # Non-staff users can only view their assigned location
    if not request.user.is_staff:
        if hasattr(request.user, 'location') and request.user.location:
            if location_id and location_id != request.user.location.id:
                # Trying to access a different location
                return redirect('stock:overview_location', location_id=request.user.location.id)
            location_id = request.user.location.id
        else:
            # User has no assigned location
            return redirect('inventory:index')

    if location_id:
        selected_location = get_object_or_404(Location, id=location_id, is_active=True)
        locations = [selected_location]
    else:
        selected_location = None
        # Only staff can view all locations
        if request.user.is_staff:
            locations = Location.objects.filter(is_active=True)
        else:
            locations = []

    # Get stock summary by location
    location_summaries = [get_location_stock_summary(loc) for loc in locations]
    total_items = sum(s['item_count'] for s in location_summaries)
    total_liters = sum(s['total_liters'] for s in location_summaries)

    # Get recent stock counts, filtered by location if specified
    if location_id:
        recent_counts = StockCount.objects.filter(location_id=location_id).order_by('-timestamp')[:30]
    else:
        recent_counts = StockCount.objects.all().order_by('-timestamp')[:10]

    # Get all beverages for table columns (or charts if location selected)
    if location_id:
        all_beverages = Beverage.objects.filter(
            is_active=True,
            available_locations=selected_location
        ).order_by(Lower('name'))
    else:
        all_beverages = Beverage.objects.filter(is_active=True).order_by(Lower('name'))

    # Prepare count data with beverage quantities
    count_data = []
    for count in recent_counts:
        count_items = {item.beverage.id: item.quantity for item in count.items.all()}
        count_data.append({
            'count': count,
            'beverages': {beverage.id: count_items.get(beverage.id, 0) for beverage in all_beverages}
        })

    # Prepare chart data for location view
    chart_data = None
    if location_id and recent_counts:
        chart_data = prepare_chart_data_for_location(selected_location, recent_counts)

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
        'current_time': timezone.now(),
    }

    return render(request, 'stock/overview.html', context)


def location_detail(request, location_id):
    """Show all beverages for a specific location with current stock."""
    # Check authentication
    if not request.user.is_authenticated:
        return redirect('inventory:not_logged_in')

    location = get_object_or_404(Location, id=location_id, is_active=True)

    # Non-staff users can only access their assigned location
    if not request.user.is_staff:
        if not (hasattr(request.user, 'location') and request.user.location and request.user.location.id == location_id):
            # User trying to access a location they're not assigned to
            if hasattr(request.user, 'location') and request.user.location:
                return redirect('stock:location_detail', location_id=request.user.location.id)
            return redirect('inventory:index')

    stock_data = get_or_create_stock_for_location(location)

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
        updated_by = request.POST.get('updated_by', 'User')
        stock = update_stock_quantity(stock, new_quantity, updated_by)

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
        adjustment = request.POST.get('adjustment', '0')
        updated_by = request.POST.get('updated_by', 'User')
        stock = adjust_stock_quantity(stock, adjustment, updated_by)

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
        # Get all current stock for this location
        stocks = Stock.objects.filter(location=location, beverage__is_active=True)

        # Create stock count using utility function
        stock_count = create_stock_count(
            location=location,
            stocks=stocks
        )

        messages.success(request, f'Stock count saved successfully! {stocks.count()} items recorded.')
        return redirect('stock:location_detail', location_id=location_id)
    except Exception as e:
        messages.error(request, f'Error saving count: {str(e)}')
        return redirect('stock:location_detail', location_id=location_id)
