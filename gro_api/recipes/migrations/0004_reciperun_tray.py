# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20150810_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='reciperun',
            name='tray',
            field=models.ForeignKey(to='layout.Tray', related_name='recipe_runs+', default=0),
            preserve_default=False,
        ),
    ]
