# Generated by Django 5.1.1 on 2024-11-16 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_category_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='created_at',
            new_name='updated_at',
        ),
    ]
