# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0002_auto_20150810_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planttype',
            name='parent',
            field=models.ForeignKey(null=True, to='plants.PlantType', related_name='children'),
        ),
    ]
