# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActuatorType',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, serialize=False, auto_created=True,
                    verbose_name='ID'
                )),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('resource_type', models.ForeignKey(
                    to='resources.ResourceType',
                )),
                ('properties', models.ManyToManyField(
                    to='resources.ResourceProperty'
                )),
                ('order', models.PositiveIntegerField()),
                ('is_binary', models.BooleanField()),
                ('effect_on_active', models.IntegerField()),
                ('read_only', models.BooleanField(
                    default=False, editable=False
                )),
                ('actuator_creation_count', models.PositiveIntegerField(
                    editable=False, default=1
                )),
            ],
            options={},
        ),
        migrations.CreateModel(
            name='Actuator',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, serialize=False, auto_created=True,
                    verbose_name='ID'
                )),
                ('index', models.PositiveIntegerField(
                    editable=False
                )),
                ('name', models.CharField(max_length=100, blank=True)),
                ('actuator_type', models.ForeignKey(
                    to='actuators.ActuatorType', related_name='actuators'
                )),
                ('resource', models.ForeignKey(
                    to='resources.Resource', related_name='actuators'
                )),
            ],
            options={
                'unique_together': set([('index', 'actuator_type')]),
            },
        ),
        migrations.CreateModel(
            name='ActuatorState',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, serialize=False, auto_created=True,
                    verbose_name='ID'
                )),
                ('timestamp', models.IntegerField()),
                ('value', models.FloatField()),
                ('origin', models.ForeignKey(
                    related_name='state+', to='actuators.Actuator'
                )),
            ],
            options={
                'get_latest_by': 'timestamp',
                'ordering': ['timestamp'],
            },
        ),
    ]
