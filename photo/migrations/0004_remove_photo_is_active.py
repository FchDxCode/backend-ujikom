# Generated by Django 5.1 on 2024-10-24 03:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0003_photo_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='is_active',
        ),
    ]
