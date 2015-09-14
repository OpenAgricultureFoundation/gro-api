# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0006_auto_20150810_0040'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='plantevent',
            options={'managed': True},
        ),
        migrations.AddField(
            model_name='planteventtype',
            name='dependencies',
            field=models.ManyToManyField(to='plants.PlantEventType', related_name='dependencies_rel_+'),
        ),
        migrations.AddField(
            model_name='planteventtype',
            name='repeatable',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='plantevent',
            name='plant',
            field=models.ForeignKey(to='plants.Plant', related_name='events'),
        ),
        migrations.AlterField(
            model_name='plantevent',
            name='site',
            field=models.ForeignKey(to='layout.PlantSite', related_name='events+'),
        ),
    ]
