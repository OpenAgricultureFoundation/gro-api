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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ActuatorState',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('timestamp', models.IntegerField()),
                ('value', models.FloatField()),
                ('origin', models.ForeignKey(related_name='state+', to='actuators.Actuator')),
            ],
            options={
                'get_latest_by': 'timestamp',
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ActuatorType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('read_only', models.BooleanField(default=False, editable=False)),
                ('properties', models.ManyToManyField(related_name='actuator_types', to='resources.ResourceProperty')),
            ],
            options={
                'managed': True,
                'abstract': False,
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
