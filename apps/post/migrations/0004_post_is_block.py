# Generated by Django 3.2.6 on 2021-12-20 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0003_alter_post_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_block',
            field=models.BooleanField(default=False),
        ),
    ]
