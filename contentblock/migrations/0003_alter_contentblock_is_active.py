# Generated by Django 5.1 on 2024-10-23 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contentblock', '0002_remove_contentblock_video_contentblock_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentblock',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
