# Generated by Django 3.2.6 on 2021-12-20 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0004_post_is_block'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='is_block',
            new_name='is_blocked',
        ),
    ]