from django.core.validators import MinValueValidator
from django.db import models
from apps.post.models import Post


class Cart(models.Model):
    user = models.IntegerField(validators=[MinValueValidator(1)])
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='carts')

    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])


class OrderDetail(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='order_details')
    payment = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    buyer = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=1, validators=[MinValueValidator(1)])
