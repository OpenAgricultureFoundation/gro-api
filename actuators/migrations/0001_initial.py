# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actuator',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ActuatorType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('properties', models.ManyToManyField(to='resources.ResourceProperty', related_name='actuator_types')),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='actuator',
            name='actuator_type',
            field=models.ForeignKey(related_name='actuators', to='actuators.ActuatorType'),
        ),
        migrations.AddField(
            model_name='actuator',
            name='resource',
            field=models.ForeignKey(related_name='actuators', to='resources.Resource'),
        ),
    ]
