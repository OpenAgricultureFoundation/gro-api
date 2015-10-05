# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0003_actuatorcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='actuatorcode',
            name='read_only',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
