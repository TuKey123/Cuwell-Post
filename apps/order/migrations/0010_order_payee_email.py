# Generated by Django 3.2.6 on 2021-12-15 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_auto_20211215_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payee_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]