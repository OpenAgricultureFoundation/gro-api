# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0004_auto_20150810_0037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantevent',
            name='timestamp',
            field=models.IntegerField(default=time.time, blank=True),
        ),
    ]
