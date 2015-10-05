# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20150902_1801'),
        ('actuators', '0005_auto_20150902_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='actuator',
            name='current_override',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, editable=False, related_name='+', null=True, to='recipes.ActuatorOverride'),
        ),
        migrations.AddField(
            model_name='actuatorstate',
            name='actuator',
            field=models.ForeignKey(default=1, to='actuators.Actuator', related_name='states+'),
            preserve_default=False,
        ),
    ]
