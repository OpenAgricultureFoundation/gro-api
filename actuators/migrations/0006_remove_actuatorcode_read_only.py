# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0005_auto_20150811_1855'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actuatorcode',
            name='read_only',
        ),
    ]
