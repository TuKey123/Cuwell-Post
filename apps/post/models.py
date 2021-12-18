from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 1
        SELL = 2
        BLOCKED = 3

    user = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.FloatField()
    status = models.IntegerField(choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)])


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    url = models.ImageField(upload_to='posts/', blank=True)


class ReportType(models.Model):
    class Type(models.IntegerChoices):
        SPAM = 1
        CHEAT = 2

    type = models.IntegerField(choices=Type.choices, default=Type.SPAM)
    description = models.CharField(max_length=300)

    def __str__(self):
        if self.type == self.Type.SPAM:
            return 'Spam'
        return 'Cheat'


class PostReport(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    report = models.ForeignKey(ReportType, on_delete=models.CASCADE, related_name='reposts')

    user = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=300)
