# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_reciperun_tray'),
    ]

    operations = [
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
    ]
