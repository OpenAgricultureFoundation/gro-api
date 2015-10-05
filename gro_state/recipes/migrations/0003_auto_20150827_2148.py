# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20150819_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='plant_types',
            field=models.ManyToManyField(blank=True, to='plants.PlantType', related_name='recipes'),
        ),
    ]
