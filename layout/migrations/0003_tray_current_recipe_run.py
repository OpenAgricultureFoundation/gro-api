# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20150811_1855'),
        ('layout', '0002_generate_dynamic_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='tray',
            name='current_recipe_run',
            field=models.ForeignKey(null=True, to='recipes.RecipeRun', related_name='+'),
        ),
    ]
