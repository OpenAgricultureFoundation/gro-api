# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0007_auto_20150510_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='main_tray',
            name='parent',
            field=models.ForeignKey(to='layout.main_bay', related_name='children'),
        ),
    ]
