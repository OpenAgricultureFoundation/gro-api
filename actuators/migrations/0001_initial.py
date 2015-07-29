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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ActuatorType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('properties', models.ManyToManyField(to='resources.ResourceProperty', related_name='actuator_types')),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='actuator',
            name='actuator_type',
            field=models.ForeignKey(to='actuators.ActuatorType', related_name='actuators'),
        ),
        migrations.AddField(
            model_name='actuator',
            name='resource',
            field=models.ForeignKey(to='resources.Resource', related_name='actuators'),
        ),
    ]
