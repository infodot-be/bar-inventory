from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Location, Beverage, Stock
from decimal import Decimal


def index(request):
    """Home page - select a location to manage inventory."""
    locations = Location.objects.filter(is_active=True)
    return render(request, 'inventory/index.html', {'locations': locations})


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
