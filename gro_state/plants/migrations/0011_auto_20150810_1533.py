# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0010_auto_20150810_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantcomment',
            name='timestamp',
            field=models.IntegerField(editable=False, default=time.time),
        ),
    ]
