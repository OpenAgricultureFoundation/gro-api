# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0011_auto_20150810_1533'),
        ('recipes', '0002_auto_20150810_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='plant_type',
        ),
        migrations.AddField(
            model_name='recipe',
            name='plant_type',
            field=models.ManyToManyField(to='plants.PlantType', related_name='recipes'),
        ),
    ]
