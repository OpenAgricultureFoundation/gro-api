# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resourceproperty',
            name='read_only',
        ),
        migrations.RemoveField(
            model_name='resourcetype',
            name='read_only',
        ),
        migrations.AddField(
            model_name='resourceproperty',
            name='max_operating_value',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='resourceproperty',
            name='min_operating_value',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
