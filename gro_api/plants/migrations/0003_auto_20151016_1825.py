# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0002_auto_20150819_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planttype',
            name='model',
            field=models.ForeignKey(null=True, to='plants.PlantModel', related_name='plant_types'),
        ),
    ]
