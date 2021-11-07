from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt import views as jwt_views

posts = DefaultRouter()
posts.register('', views.PostCreateViewSet)

categories = DefaultRouter()
categories.register('', views.CategoryViewSet)

report_types = DefaultRouter()
report_types.register('', views.ReportTypeViewSet)

post_reports = DefaultRouter()
post_reports.register('', views.PostReportViewSet)

urlpatterns = [
    path('api/login/', jwt_views.TokenObtainPairView.as_view(), name='login'),
    path('posts/', include(posts.urls)),
    path('categories/', include(categories.urls)),
    path('report-types/', include(report_types.urls)),
    path('post-reposts/', include(post_reports.urls)),
]
