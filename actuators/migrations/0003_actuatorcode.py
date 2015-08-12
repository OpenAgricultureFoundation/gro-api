# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0002_setup'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActuatorCode',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('val', models.CharField(max_length=2)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
    ]
