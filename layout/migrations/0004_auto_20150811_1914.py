# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0003_tray_current_recipe_run'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tray',
            name='current_recipe_run',
            field=models.ForeignKey(null=True, related_name='+', to='recipes.RecipeRun', editable=False, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
