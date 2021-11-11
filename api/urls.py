from django.urls import path
from django.urls.conf import include
from apps.post import urls as post_urls
from apps.order import urls as order_urls

urlpatterns = [
    path('', include(post_urls)),
    path('orders/', include(order_urls))
]
