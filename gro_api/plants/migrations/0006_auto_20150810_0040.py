# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0005_auto_20150810_0038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantevent',
            name='timestamp',
            field=models.IntegerField(default=time.time, editable=False),
        ),
    ]
