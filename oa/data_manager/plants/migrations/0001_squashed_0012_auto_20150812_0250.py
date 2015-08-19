# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    replaces = [('plants', '0001_initial'), ('plants', '0002_auto_20150810_0023'), ('plants', '0003_auto_20150810_0028'), ('plants', '0004_auto_20150810_0037'), ('plants', '0005_auto_20150810_0038'), ('plants', '0006_auto_20150810_0040'), ('plants', '0007_auto_20150810_0058'), ('plants', '0008_auto_20150810_0100'), ('plants', '0009_auto_20150810_1520'), ('plants', '0010_auto_20150810_1522'), ('plants', '0011_auto_20150810_1533'), ('plants', '0012_auto_20150812_0250')]

    dependencies = [
        ('layout', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sown_date', models.DateTimeField()),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PlantType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('common_name', models.CharField(max_length=100)),
                ('latin_name', models.CharField(max_length=100)),
                ('parent', models.ForeignKey(to='plants.PlantType', default=9, related_name='children')),
                ('plant_count', models.PositiveIntegerField(default=0, editable=False)),
                ('read_only', models.BooleanField(default=False, editable=False)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='plant',
            name='plant_type',
            field=models.ForeignKey(to='plants.PlantType', related_name='plants'),
        ),
        migrations.AddField(
            model_name='plant',
            name='site',
            field=models.OneToOneField(to='layout.PlantSite', related_name='plant', null=True),
        ),
        migrations.CreateModel(
            name='PlantComment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.IntegerField(default=time.time)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PlantModel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='plant_models')),
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
        migrations.AddField(
            model_name='plant',
            name='index',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plantcomment',
            name='plant',
            field=models.ForeignKey(to='plants.Plant', related_name='comments'),
        ),
        migrations.AddField(
            model_name='planttype',
            name='model',
            field=models.ForeignKey(to='plants.PlantModel', default=0, related_name='plant_types'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='planttype',
            name='parent',
            field=models.ForeignKey(to='plants.PlantType', related_name='children', null=True),
        ),
        migrations.CreateModel(
            name='HarvestEvent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.IntegerField(default=time.time)),
                ('plant', models.OneToOneField(to='plants.Plant', related_name='harvest_event')),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SowEvent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.IntegerField(default=time.time)),
                ('plant', models.OneToOneField(to='plants.Plant', related_name='sow_event')),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TransferEvent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.IntegerField(default=time.time)),
                ('from_site', models.ForeignKey(to='layout.PlantSite', related_name='+')),
                ('plant', models.ForeignKey(to='plants.Plant', related_name='transfer_events')),
                ('to_site', models.ForeignKey(to='layout.PlantSite', related_name='+')),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='sowevent',
            name='site',
            field=models.ForeignKey(to='layout.PlantSite', related_name='sow_events+'),
        ),
        migrations.AlterField(
            model_name='plantcomment',
            name='timestamp',
            field=models.IntegerField(default=time.time, editable=False),
        ),
        migrations.RemoveField(
            model_name='planttype',
            name='read_only',
        ),
    ]
