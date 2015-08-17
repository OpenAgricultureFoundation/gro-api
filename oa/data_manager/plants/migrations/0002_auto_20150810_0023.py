# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0001_initial'),
        ('plants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlantComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('timestamp', models.IntegerField(default=time.time)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PlantEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('timestamp', models.IntegerField(default=time.time)),
            ],
            options={
                'default_related_name': 'events',
            },
        ),
        migrations.CreateModel(
            name='PlantEventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('read_only', models.BooleanField(editable=False, default=False)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PlantModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='plant_models')),
                ('read_only', models.BooleanField(editable=False, default=False)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.RemoveField(
            model_name='plant',
            name='sown_date',
        ),
        migrations.RemoveField(
            model_name='planttype',
            name='plant_size',
        ),
        migrations.AddField(
            model_name='plant',
            name='in_system',
            field=models.BooleanField(editable=False, default=False),
        ),
        migrations.AddField(
            model_name='plant',
            name='index',
            field=models.PositiveIntegerField(editable=False, default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='planttype',
            name='parent',
            field=models.ForeignKey(related_name='children', default=9, to='plants.PlantType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='planttype',
            name='plant_count',
            field=models.PositiveIntegerField(editable=False, default=0),
        ),
        migrations.AddField(
            model_name='planttype',
            name='read_only',
            field=models.BooleanField(editable=False, default=False),
        ),
        migrations.AddField(
            model_name='plantevent',
            name='event_type',
            field=models.ForeignKey(related_name='events+', to='plants.PlantEventType'),
        ),
        migrations.AddField(
            model_name='plantevent',
            name='plant',
            field=models.ForeignKey(to='plants.Plant'),
        ),
        migrations.AddField(
            model_name='plantevent',
            name='site',
            field=models.OneToOneField(to='layout.PlantSite'),
        ),
        migrations.AddField(
            model_name='plantcomment',
            name='plant',
            field=models.ForeignKey(related_name='comments', to='plants.Plant'),
        ),
        migrations.AddField(
            model_name='planttype',
            name='model',
            field=models.ForeignKey(related_name='plant_types', default=0, to='plants.PlantModel'),
            preserve_default=False,
        ),
    ]
