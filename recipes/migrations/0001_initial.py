# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0001_initial'), ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='recipes')),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RecipeRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_timestamp', models.IntegerField()),
                ('recipe', models.ForeignKey(to='recipes.Recipe', related_name='runs')),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SetPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.IntegerField()),
                ('value', models.FloatField()),
                ('property', models.ForeignKey(to='resources.ResourceProperty', related_name='set_points+')),
                ('tray', models.ForeignKey(to='layout.Tray', related_name='set_points+')),
            ],
            options={
                'get_latest_by': 'timestamp',
            },
        ),
    ]
