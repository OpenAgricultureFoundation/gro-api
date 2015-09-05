# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0004_auto_20150819_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actuator',
            name='override_timeout',
        ),
        migrations.RemoveField(
            model_name='actuator',
            name='override_value',
        ),
        migrations.RemoveField(
            model_name='actuatorstate',
            name='origin',
        ),
    ]
