# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0009_auto_20150810_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='site',
            field=models.OneToOneField(to='layout.PlantSite', related_name='plant', null=True),
        ),
    ]
