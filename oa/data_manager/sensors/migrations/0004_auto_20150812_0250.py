# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0003_auto_20150810_1707'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensortype',
            name='read_only',
        ),
        migrations.AddField(
            model_name='sensingpoint',
            name='auto_created',
            field=models.BooleanField(editable=False, default=False),
        ),
        migrations.AddField(
            model_name='sensingpoint',
            name='is_pseudo',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='sensingpoint',
            name='sensor',
            field=models.ForeignKey(to='sensors.Sensor', null=True),
        ),
    ]
