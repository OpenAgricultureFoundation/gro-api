# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20150811_2201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='plant_type',
            new_name='plant_types',
        ),
        migrations.AlterField(
            model_name='reciperun',
            name='start_timestamp',
            field=models.IntegerField(blank=True),
        ),
    ]
