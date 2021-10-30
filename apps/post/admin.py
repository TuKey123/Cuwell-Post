from django.contrib import admin
from .models import Post, Category, PostImage, ReportType, PostReport

# Register your models here.
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(ReportType)
admin.site.register(PostReport)
