# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20150811_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setpoint',
            name='value',
            field=models.FloatField(null=True),
        ),
    ]
