# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0007_auto_20150810_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planteventtype',
            name='dependencies',
            field=models.ManyToManyField(to='plants.PlantEventType', related_name='dependents'),
        ),
    ]
