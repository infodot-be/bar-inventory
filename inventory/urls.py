from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.index, name='index'),
    path('location/<int:location_id>/', views.location_detail, name='location_detail'),
    path('stock/<int:stock_id>/update/', views.update_stock, name='update_stock'),
    path('stock/<int:stock_id>/adjust/', views.quick_adjust, name='quick_adjust'),
]
