# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapoint',
            name='timestamp',
            field=models.IntegerField(blank=True, default=time.time),
        ),
    ]
