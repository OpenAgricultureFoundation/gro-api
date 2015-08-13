# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20150811_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reciperun',
            name='end_timestamp',
            field=models.IntegerField(blank=True),
        ),
    ]
