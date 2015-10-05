# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0005_auto_20150902_1801'),
        ('recipes', '0003_auto_20150827_2148'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActuatorOverride',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('start_timestamp', models.IntegerField(default=time.time, blank=True)),
                ('end_timestamp', models.IntegerField(blank=True)),
                ('value', models.FloatField()),
                ('actuator', models.ForeignKey(related_name='overrides+', to='actuators.Actuator')),
            ],
            options={
                'ordering': ['start_timestamp'],
                'get_latest_by': 'start_timestamp',
            },
        ),
        migrations.AlterModelOptions(
            name='reciperun',
            options={'ordering': ['start_timestamp'], 'get_latest_by': 'start_timestamp'},
        ),
        migrations.AlterModelOptions(
            name='setpoint',
            options={'ordering': ['timestamp'], 'get_latest_by': 'timestamp'},
        ),
        migrations.AlterField(
            model_name='reciperun',
            name='start_timestamp',
            field=models.IntegerField(default=time.time, blank=True),
        ),
    ]
