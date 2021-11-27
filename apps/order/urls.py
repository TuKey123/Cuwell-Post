from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

carts = DefaultRouter()
carts.register('', views.CartViewSet)

orders = DefaultRouter()
orders.register('', views.OrderViewSet)
