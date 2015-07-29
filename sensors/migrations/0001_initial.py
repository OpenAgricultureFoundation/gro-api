# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('value', models.FloatField()),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SensingPoint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('property', models.ForeignKey(related_name='sensing_points', to='resources.ResourceProperty')),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('resource', models.ForeignKey(related_name='sensors', to='resources.Resource')),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SensorType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('properties', models.ManyToManyField(related_name='sensor_types', to='resources.ResourceProperty')),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='sensor',
            name='sensor_type',
            field=models.ForeignKey(related_name='sensors', to='sensors.SensorType'),
        ),
        migrations.AddField(
            model_name='sensingpoint',
            name='sensor',
            field=models.ForeignKey(related_name='sensing_points', to='sensors.Sensor'),
        ),
        migrations.AddField(
            model_name='datapoint',
            name='origin',
            field=models.ForeignKey(related_name='data_points', to='sensors.SensingPoint'),
        ),
    ]
