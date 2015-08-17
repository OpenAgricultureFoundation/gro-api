# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0008_auto_20150812_1550'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ActuatorCode',
            new_name='ActuatorClass',
        ),
        migrations.RenameField(
            model_name='actuatorclass',
            old_name='val',
            new_name='code',
        ),
        migrations.RenameField(
            model_name='actuatorclass',
            old_name='description',
            new_name='name',
        ),
        migrations.AddField(
            model_name='actuatortype',
            name='actuator_class',
            field=models.ForeignKey(to='actuators.ActuatorClass', default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='controlprofile',
            name='properties',
            field=models.ManyToManyField(to='resources.ResourceProperty', through='actuators.ActuatorEffect', related_name='+'),
        ),
        migrations.AlterUniqueTogether(
            name='actuatortype',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='code',
        ),
    ]
