# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0011_auto_20150810_1533'),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='plant_type',
            field=models.ForeignKey(to='plants.PlantType', default=0, related_name='recipes'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='reciperun',
            name='start_timestamp',
            field=models.IntegerField(default=time.time, blank=True),
        ),
    ]
