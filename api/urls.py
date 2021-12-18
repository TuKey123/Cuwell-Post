from django.urls import path
from django.urls.conf import include
from apps.post import urls as post_urls
from apps.order.urls import carts, seller, buyer, payment

urlpatterns = [
    path('', include(post_urls)),
    path('carts/', include(carts.urls)),
    path('seller/', include(seller.urls)),
    path('buyer/', include(buyer.urls)),
    path('payment/', include(payment.urls)),
]
