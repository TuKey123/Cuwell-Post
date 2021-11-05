from django.urls import path
from django.urls.conf import include
from apps.post import urls

urlpatterns = [
    path('', include(urls))
]
