# Generated by Django 5.1.1 on 2024-11-17 10:59

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stats', models.JSONField()),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
