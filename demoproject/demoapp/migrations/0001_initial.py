# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventCaptureVideos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('evntname', models.CharField(max_length=150, blank=True)),
                ('path', models.CharField(max_length=550, blank=True)),
                ('created_at', models.CharField(max_length=50)),
                ('updated_at', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'EventVideos',
            },
        ),
        migrations.CreateModel(
            name='TagUserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(unique=True, max_length=100)),
                ('name', models.CharField(max_length=150, blank=True)),
                ('mobile', models.CharField(max_length=15, blank=True)),
                ('occupation', models.CharField(max_length=15, blank=True)),
                ('image', models.ImageField(null=True, upload_to=b'user_uploads')),
                ('created_at', models.CharField(max_length=50)),
                ('updated_at', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'TagUserInfo',
            },
        ),
        migrations.CreateModel(
            name='VideoCaptured',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=100)),
                ('image', models.ImageField(null=True, upload_to=b'user_uploads')),
                ('status', models.CharField(max_length=50, blank=True)),
                ('name', models.CharField(max_length=150, blank=True)),
                ('occupation', models.CharField(max_length=15, blank=True)),
                ('created_at', models.CharField(max_length=50)),
                ('updated_at', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'VideoCaptured',
            },
        ),
    ]
