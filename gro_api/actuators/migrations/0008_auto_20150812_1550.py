# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0007_auto_20150812_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actuatoreffect',
            name='control_profile',
            field=models.ForeignKey(to='actuators.ControlProfile', related_name='effects'),
        ),
        migrations.AlterField(
            model_name='actuatoreffect',
            name='effect_on_active',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='actuatoreffect',
            name='property',
            field=models.ForeignKey(to='resources.ResourceProperty', related_name='+'),
        ),
        migrations.AlterField(
            model_name='actuatoreffect',
            name='threshold',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='controlprofile',
            name='properties',
            field=models.ManyToManyField(through='actuators.ActuatorEffect', editable=False, to='resources.ResourceProperty', related_name='+'),
        ),
    ]
