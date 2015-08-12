# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_auto_20150811_2307'),
        ('actuators', '0006_remove_actuatorcode_read_only'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActuatorEffect',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('effect_on_active', models.FloatField()),
                ('threshold', models.FloatField()),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ControlProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('period', models.FloatField()),
                ('pulse_width', models.FloatField()),
            ],
            options={
                'managed': True,
                'abstract': False,
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
            model_name='actuatorcode',
            name='description',
            field=models.CharField(unique=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='actuatorcode',
            name='val',
            field=models.CharField(unique=True, max_length=2),
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
            field=models.ManyToManyField(through='actuators.ActuatorEffect', to='resources.ResourceProperty'),
        ),
        migrations.AddField(
            model_name='actuatoreffect',
            name='control_profile',
            field=models.ForeignKey(to='actuators.ControlProfile'),
        ),
        migrations.AddField(
            model_name='actuatoreffect',
            name='property',
            field=models.ForeignKey(to='resources.ResourceProperty'),
        ),
        migrations.AddField(
            model_name='actuator',
            name='control_profile',
            field=models.ForeignKey(default=0, to='actuators.ControlProfile'),
            preserve_default=False,
        ),
    ]
