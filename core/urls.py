from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.api_register, name='api_register'),
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('cart/', views.cart_view, name='cart'),
    path('suggestions/', views.suggestions_view, name='suggestions'),
]