# Generated by Django 3.2.6 on 2021-12-15 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_remove_order_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='payee_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]