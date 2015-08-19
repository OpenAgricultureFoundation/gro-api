# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0005_resourceeffect_read_only'),
        ('actuators', '0001_squashed_0011_auto_20150813_0433'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='actuatorclass',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='actuatorclass',
            name='resource_type',
        ),
        migrations.AlterModelOptions(
            name='actuatoreffect',
            options={},
        ),
        migrations.AlterModelOptions(
            name='controlprofile',
            options={},
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='actuator_class',
        ),
        migrations.AddField(
            model_name='actuatortype',
            name='resource_effect',
            field=models.ForeignKey(to='resources.ResourceEffect', default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='actuatorstate',
            name='timestamp',
            field=models.IntegerField(blank=True, default=time.time),
        ),
        migrations.DeleteModel(
            name='ActuatorClass',
        ),
    ]
