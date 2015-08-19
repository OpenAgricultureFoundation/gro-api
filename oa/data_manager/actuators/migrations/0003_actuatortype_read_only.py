# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0002_auto_20150819_0025'),
    ]

    operations = [
        migrations.AddField(
            model_name='actuatortype',
            name='read_only',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
