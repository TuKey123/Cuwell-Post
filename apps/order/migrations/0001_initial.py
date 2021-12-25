# Generated by Django 3.2.6 on 2021-12-25 16:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer', models.CharField(max_length=200)),
                ('payment_id', models.CharField(blank=True, max_length=100)),
                ('payer_id', models.CharField(blank=True, max_length=100)),
                ('authentication', models.IntegerField(choices=[(1, 'Active'), (2, 'Inactive')], default=2)),
                ('checkout', models.BooleanField(default=False)),
                ('street', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payee_email', models.EmailField(max_length=254, null=True)),
                ('description', models.CharField(max_length=200, null=True)),
                ('price', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('delivery_day', models.DateField(null=True)),
                ('status', models.IntegerField(choices=[(1, 'Delivered'), (2, 'Waiting'), (3, 'Accepted'), (4, 'Cancel')], default=2)),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='order.payment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='post.post')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=200)),
                ('quantity', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('payee_email', models.EmailField(max_length=254, null=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='post.post')),
            ],
        ),
    ]
