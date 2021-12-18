from django.core.validators import MinValueValidator
from django.db import models
from apps.post.models import Post


class Cart(models.Model):
    user = models.CharField(max_length=200)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='carts')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    payee_email = models.EmailField(null=True)


class Payment(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 1
        INACTIVE = 2

    buyer = models.CharField(max_length=200)
    payment_id = models.CharField(max_length=100, blank=True)
    payer_id = models.CharField(max_length=100, blank=True)
    authentication = models.IntegerField(choices=Status.choices, default=Status.INACTIVE)
    checkout = models.BooleanField(default=False)
    street = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)


class Order(models.Model):
    class Status(models.IntegerChoices):
        DELIVERED = 1
        WAITING = 2
        ACCEPTED = 3
        CANCEL = 4

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='orders')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True)

    payee_email = models.EmailField(null=True)
    description = models.CharField(max_length=200, null=True)
    price = models.FloatField(validators=[MinValueValidator(0)], null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now=True)
    delivery_day = models.DateField(null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.WAITING)
