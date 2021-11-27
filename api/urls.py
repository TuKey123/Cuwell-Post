from django.urls import path
from django.urls.conf import include
from apps.post import urls as post_urls
from apps.order.urls import carts, orders

urlpatterns = [
    path('', include(post_urls)),
    path('orders/', include(orders.urls)),
    path('carts/', include(carts.urls))
]
