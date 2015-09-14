# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [('actuators', '0001_initial'), ('actuators', '0003_actuatorcode'), ('actuators', '0004_actuatorcode_read_only'), ('actuators', '0005_auto_20150811_1855'), ('actuators', '0006_remove_actuatorcode_read_only'), ('actuators', '0007_auto_20150812_1520'), ('actuators', '0008_auto_20150812_1550'), ('actuators', '0009_auto_20150812_1656'), ('actuators', '0010_auto_20150812_1907'), ('actuators', '0011_auto_20150813_0433')]

    dependencies = [
        ('resources', '0003_auto_20150811_2307'),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActuatorType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=100)),
                ('resource_type', models.ForeignKey(to='resources.ResourceType')),
                ('properties', models.ManyToManyField(to='resources.ResourceProperty')),
                ('order', models.PositiveIntegerField()),
                ('is_binary', models.BooleanField()),
                ('effect_on_active', models.IntegerField()),
                ('read_only', models.BooleanField(default=False, editable=False)),
                ('actuator_count', models.PositiveIntegerField(default=0, editable=False)),
                ('threshold', models.FloatField(default=0)),
                ('operating_range_min', models.FloatField(default=0)),
                ('operating_range_max', models.FloatField(default=0)),
            ],
            options={
                'unique_together': set([('code', 'resource_type'), ('name', 'resource_type')]),
            },
        ),
        migrations.CreateModel(
            name='Actuator',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('index', models.PositiveIntegerField(editable=False)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('actuator_type', models.ForeignKey(to='actuators.ActuatorType', related_name='actuators')),
                ('resource', models.ForeignKey(to='resources.Resource', related_name='actuators')),
                ('override_value', models.FloatField(editable=False, null=True)),
                ('override_timeout', models.IntegerField(editable=False, null=True)),
            ],
            options={
                'unique_together': set([('index', 'actuator_type')]),
            },
        ),
        migrations.CreateModel(
            name='ActuatorState',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('timestamp', models.IntegerField()),
                ('value', models.FloatField()),
                ('origin', models.ForeignKey(to='actuators.Actuator', related_name='state+')),
            ],
            options={
                'get_latest_by': 'timestamp',
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ActuatorClass',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=2, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.AlterField(
            model_name='actuatortype',
            name='code',
            field=models.CharField(max_length=2, choices=[('HE', 'HE'), ('VE', 'VE')]),
        ),
        migrations.CreateModel(
            name='ActuatorEffect',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('effect_on_active', models.FloatField()),
                ('threshold', models.FloatField()),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ControlProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('period', models.FloatField()),
                ('pulse_width', models.FloatField()),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='effect_on_active',
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='operating_range_max',
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='operating_range_min',
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='read_only',
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='threshold',
        ),
        migrations.AlterField(
            model_name='actuator',
            name='actuator_type',
            field=models.ForeignKey(to='actuators.ActuatorType'),
        ),
        migrations.AlterField(
            model_name='actuatortype',
            name='code',
            field=models.CharField(max_length=2),
        ),
        migrations.AddField(
            model_name='controlprofile',
            name='actuator_type',
            field=models.ForeignKey(to='actuators.ActuatorType', related_name='allowed_control_profiles'),
        ),
        migrations.AddField(
            model_name='controlprofile',
            name='properties',
            field=models.ManyToManyField(to='resources.ResourceProperty', through='actuators.ActuatorEffect'),
        ),
        migrations.AddField(
            model_name='actuatoreffect',
            name='control_profile',
            field=models.ForeignKey(to='actuators.ControlProfile', related_name='effects'),
        ),
        migrations.AddField(
            model_name='actuatoreffect',
            name='property',
            field=models.ForeignKey(to='resources.ResourceProperty', related_name='+'),
        ),
        migrations.AddField(
            model_name='actuator',
            name='control_profile',
            field=models.ForeignKey(to='actuators.ControlProfile', default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='actuatoreffect',
            name='effect_on_active',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='actuatoreffect',
            name='threshold',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='actuatortype',
            name='actuator_class',
            field=models.ForeignKey(to='actuators.ActuatorClass', default=0),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='actuatortype',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='actuatortype',
            name='code',
        ),
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
            field=models.ForeignKey(to='resources.ResourceType', default=0),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='actuatorclass',
            unique_together=set([('code', 'resource_type'), ('name', 'resource_type')]),
        ),
    ]
