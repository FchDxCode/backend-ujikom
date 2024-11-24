# Generated by Django 5.1 on 2024-09-26 12:48

import django.db.models.deletion
import photo.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('album', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('photo', models.ImageField(upload_to=photo.models.get_album_upload_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('sequence_number', models.PositiveIntegerField(blank=True, null=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='album.album')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
