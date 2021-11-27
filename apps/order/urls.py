from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

carts = DefaultRouter()
carts.register('', views.CartViewSet)

order_details = DefaultRouter()
order_details.register('', views.CartViewSet)
