# Generated by Django 5.1.1 on 2024-11-13 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0004_remove_photo_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
