# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0005_auto_20150819_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enclosure',
            name='model',
            field=models.ForeignKey(null=True, to='layout.Model3D', related_name='+', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
