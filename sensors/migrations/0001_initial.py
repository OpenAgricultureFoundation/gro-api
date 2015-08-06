# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorType',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, serialize=False, verbose_name='ID',
                    primary_key=True
                )),
                ('name', models.CharField(max_length=100, unique=True)),
                ('resource_type', models.ForeignKey(
                    to='resources.ResourceType'
                )),
                ('properties', models.ManyToManyField(
                    to='resources.ResourceProperty',
                )),
                ('read_only', models.BooleanField(
                    default=False, editable=False
                )),
                ('sensor_count', models.PositiveIntegerField(
                    default=0, editable=False
                )),
            ],
            options={
            },
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, serialize=False, verbose_name='ID',
                    primary_key=True
                )),
                ('index', models.PositiveIntegerField(editable=False)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('sensor_type', models.ForeignKey(to='sensors.SensorType')),
                ('resource', models.ForeignKey(to='resources.Resource')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'unique_together': set([('index', 'sensor_type')])
            },
        ),
        migrations.CreateModel(
            name='SensingPoint',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, serialize=False, verbose_name='ID',
                    primary_key=True
                )),
                ('index', models.PositiveIntegerField(editable=False)),
                ('sensor', models.ForeignKey(to='sensors.Sensor')),
                ('property', models.ForeignKey(
                    to='resources.ResourceProperty',
                )),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'unique_together': set([('index', 'property')])
            },
        ),
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, serialize=False, verbose_name='ID',
                    primary_key=True
                )),
                ('origin', models.ForeignKey(
                    to='sensors.SensingPoint', related_name='data_points+'
                )),
                ('timestamp', models.IntegerField()),
                ('value', models.FloatField()),
            ],
            options={
                'get_latest_by': 'timestamp',
                'ordering': ['timestamp'],
            },
        ),
    ]
