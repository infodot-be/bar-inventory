from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('stock/overview/', views.stock_overview, name='overview'),
    path('stock/overview/<int:location_id>/', views.stock_overview, name='overview_location'),
    path('location/<int:location_id>/', views.location_detail, name='location_detail'),
    path('stock/<int:stock_id>/update/', views.update_stock, name='update_stock'),
    path('stock/<int:stock_id>/adjust/', views.quick_adjust, name='quick_adjust'),
    path('location/<int:location_id>/save-count/', views.save_count, name='save_count'),
]
