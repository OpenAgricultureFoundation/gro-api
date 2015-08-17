# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_auto_20150811_2307'),
        ('actuators', '0010_auto_20150812_1907'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actuatorclass',
            options={},
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='resource_type',
        ),
        migrations.AddField(
            model_name='actuatorclass',
            name='resource_type',
            field=models.ForeignKey(default=0, to='resources.ResourceType'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='actuatorclass',
            unique_together=set([('code', 'resource_type'), ('name', 'resource_type')]),
        ),
    ]
