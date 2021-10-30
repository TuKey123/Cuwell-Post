from django.contrib import admin
from .models import Cart, OrderDetail

# Register your models here.
admin.site.register(Cart)
admin.site.register(OrderDetail)