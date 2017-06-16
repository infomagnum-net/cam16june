# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demoapp', '0002_auto_20170616_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='Addcamera',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('camname', models.CharField(max_length=150, blank=True)),
                ('camip', models.CharField(max_length=550, blank=True)),
                ('purpose', models.CharField(max_length=550, blank=True)),
                ('height', models.IntegerField(max_length=550, blank=True)),
                ('width', models.IntegerField(max_length=550, blank=True)),
                ('created_at', models.CharField(max_length=50)),
                ('updated_at', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'Addcamera',
            },
        ),
        migrations.DeleteModel(
            name='TagUserInfo',
        ),
    ]
