# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0004_actuatorcode_read_only'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actuatortype',
            name='code',
            field=models.CharField(max_length=2, choices=[('HE', 'HE'), ('VE', 'VE')]),
        ),
    ]
