# Generated by Django 3.2.6 on 2021-11-12 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.CharField(max_length=200),
        ),
    ]
