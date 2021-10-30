from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from api import urls
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="POST SERVICE",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

swagger = [
    path('api/v1/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path(r'^redoc/$', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]

urlpatterns = [
    path('', include(swagger)),
    path('admin/', admin.site.urls),
]
