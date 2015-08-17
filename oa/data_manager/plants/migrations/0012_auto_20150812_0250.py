# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0011_auto_20150810_1533'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plantmodel',
            name='read_only',
        ),
        migrations.RemoveField(
            model_name='planttype',
            name='read_only',
        ),
    ]
