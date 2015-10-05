# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    replaces = [('recipes', '0001_initial'), ('recipes', '0002_auto_20150810_1606'), ('recipes', '0003_auto_20150810_1707'), ('recipes', '0004_reciperun_tray'), ('recipes', '0005_auto_20150810_1824'), ('recipes', '0006_auto_20150811_1855'), ('recipes', '0007_auto_20150811_2201'), ('recipes', '0008_auto_20150811_2225'), ('recipes', '0009_auto_20150813_0122')]

    dependencies = [
        ('plants', '0001_squashed_0012_auto_20150812_0250'),
        ('layout', '0001_initial'),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='recipes')),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecipeRun',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('start_timestamp', models.IntegerField(blank=True, default=time.time)),
                ('recipe', models.ForeignKey(to='recipes.Recipe', related_name='runs')),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SetPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('timestamp', models.IntegerField()),
                ('value', models.FloatField()),
                ('property', models.ForeignKey(to='resources.ResourceProperty', related_name='set_points+')),
                ('tray', models.ForeignKey(to='layout.Tray', related_name='set_points+')),
            ],
            options={
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='plant_types',
            field=models.ManyToManyField(to='plants.PlantType', related_name='recipes'),
        ),
        migrations.AddField(
            model_name='reciperun',
            name='tray',
            field=models.ForeignKey(to='layout.Tray', default=0, related_name='recipe_runs+'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reciperun',
            name='end_timestamp',
            field=models.IntegerField(editable=False, default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='setpoint',
            name='recipe_run',
            field=models.ForeignKey(to='recipes.RecipeRun', default=0, related_name='set_points+'),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='reciperun',
            options={'get_latest_by': 'start_timestamp'},
        ),
        migrations.AlterField(
            model_name='setpoint',
            name='value',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='reciperun',
            name='start_timestamp',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='reciperun',
            name='end_timestamp',
            field=models.IntegerField(blank=True),
        ),
    ]
