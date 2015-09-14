# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0002_sensortype_read_only'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datapoint',
            old_name='origin',
            new_name='sensing_point',
        ),
    ]
