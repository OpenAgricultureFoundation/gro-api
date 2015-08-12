# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0009_auto_20150812_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controlprofile',
            name='properties',
            field=models.ManyToManyField(through='actuators.ActuatorEffect', to='resources.ResourceProperty'),
        ),
    ]
