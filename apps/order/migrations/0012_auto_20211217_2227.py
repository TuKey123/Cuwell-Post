# Generated by Django 3.2.6 on 2021-12-17 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_alter_order_payee_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='city',
        ),
        migrations.RemoveField(
            model_name='order',
            name='district',
        ),
        migrations.RemoveField(
            model_name='order',
            name='street',
        ),
        migrations.AddField(
            model_name='payment',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='payment',
            name='district',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='payment',
            name='street',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='payee_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]