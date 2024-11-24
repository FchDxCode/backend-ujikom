# Generated by Django 5.1.1 on 2024-11-16 10:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Analytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255)),
                ('method', models.CharField(max_length=10)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('is_authenticated', models.BooleanField(default=False)),
                ('response_status', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['-timestamp'], name='analytics_a_timesta_a00036_idx'), models.Index(fields=['ip_address'], name='analytics_a_ip_addr_194822_idx'), models.Index(fields=['path'], name='analytics_a_path_aa5580_idx')],
            },
        ),
    ]
