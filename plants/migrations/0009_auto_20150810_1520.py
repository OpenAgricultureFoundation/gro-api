# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0002_generate_dynamic_models'),
        ('plants', '0008_auto_20150810_0100'),
    ]

    operations = [
        migrations.CreateModel(
            name='HarvestEvent',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('timestamp', models.IntegerField(default=time.time)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SowEvent',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('timestamp', models.IntegerField(default=time.time)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TransferEvent',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('timestamp', models.IntegerField(default=time.time)),
                ('from_site', models.ForeignKey(related_name='+', to='layout.PlantSite')),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.RemoveField(
            model_name='plantevent',
            name='event_type',
        ),
        migrations.RemoveField(
            model_name='plantevent',
            name='plant',
        ),
        migrations.RemoveField(
            model_name='plantevent',
            name='site',
        ),
        migrations.RemoveField(
            model_name='planteventtype',
            name='dependencies',
        ),
        migrations.RemoveField(
            model_name='plant',
            name='in_system',
        ),
        migrations.DeleteModel(
            name='PlantEvent',
        ),
        migrations.DeleteModel(
            name='PlantEventType',
        ),
        migrations.AddField(
            model_name='transferevent',
            name='plant',
            field=models.ForeignKey(related_name='transfer_events', to='plants.Plant'),
        ),
        migrations.AddField(
            model_name='transferevent',
            name='to_site',
            field=models.ForeignKey(related_name='+', to='layout.PlantSite'),
        ),
        migrations.AddField(
            model_name='sowevent',
            name='plant',
            field=models.OneToOneField(to='plants.Plant', related_name='sow_event'),
        ),
        migrations.AddField(
            model_name='sowevent',
            name='site',
            field=models.ForeignKey(related_name='sow_events+', to='layout.PlantSite'),
        ),
        migrations.AddField(
            model_name='harvestevent',
            name='plant',
            field=models.OneToOneField(to='plants.Plant', related_name='harvest_event'),
        ),
    ]
