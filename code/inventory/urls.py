from django.urls import path
from . import views, views_auth

app_name = 'inventory'

urlpatterns = [
    path('', views.index, name='index'),
    path('not-logged-in/', views.not_logged_in, name='not_logged_in'),
    path('token-login/<str:uidb64>/<str:token>/', views_auth.token_login, name='token_login'),
    path('generate-token/<int:location_id>/', views_auth.generate_token_link, name='generate_token'),
]
