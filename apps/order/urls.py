from rest_framework.routers import DefaultRouter
from . import views

carts = DefaultRouter()
carts.register('', views.CartViewSet)

buyer = DefaultRouter()
buyer.register('orders', views.BuyerOrderViewSet)
buyer.register('checkout', views.BuyerCheckOutViewSet)

seller = DefaultRouter()
seller.register('orders', views.SellerOrderViewSet)

payment = DefaultRouter()
payment.register('', views.PaymentViewSet)
