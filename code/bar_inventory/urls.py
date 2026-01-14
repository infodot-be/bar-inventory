"""
URL configuration for bar_inventory project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('', include('stock.urls')),
]
