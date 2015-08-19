# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    replaces = [('sensors', '0001_initial'), ('sensors', '0003_auto_20150810_1707'), ('sensors', '0004_auto_20150812_0250')]

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensorType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('resource_type', models.ForeignKey(to='resources.ResourceType')),
                ('properties', models.ManyToManyField(to='resources.ResourceProperty')),
                ('read_only', models.BooleanField(default=False, editable=False)),
                ('sensor_count', models.PositiveIntegerField(default=0, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('index', models.PositiveIntegerField(editable=False)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('sensor_type', models.ForeignKey(to='sensors.SensorType')),
                ('resource', models.ForeignKey(to='resources.Resource')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'unique_together': set([('index', 'sensor_type')]),
            },
        ),
        migrations.CreateModel(
            name='SensingPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('index', models.PositiveIntegerField(editable=False)),
                ('sensor', models.ForeignKey(to='sensors.Sensor')),
                ('property', models.ForeignKey(to='resources.ResourceProperty')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'unique_together': set([('index', 'property')]),
            },
        ),
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('origin', models.ForeignKey(to='sensors.SensingPoint', related_name='data_points+')),
                ('timestamp', models.IntegerField(default=time.time, blank=True)),
                ('value', models.FloatField()),
            ],
            options={
                'ordering': ['timestamp'],
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.RemoveField(
            model_name='sensortype',
            name='read_only',
        ),
        migrations.AddField(
            model_name='sensingpoint',
            name='auto_created',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='sensingpoint',
            name='is_pseudo',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='sensingpoint',
            name='sensor',
            field=models.ForeignKey(null=True, to='sensors.Sensor'),
        ),
    ]
