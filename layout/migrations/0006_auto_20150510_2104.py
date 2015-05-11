# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0005_auto_20150510_2058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='main_aisle',
            name='layoutobject_ptr',
        ),
        migrations.RemoveField(
            model_name='main_aisle',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='main_bay',
            name='layoutobject_ptr',
        ),
        migrations.RemoveField(
            model_name='main_bay',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='main_enclosure',
            name='layoutobject_ptr',
        ),
        migrations.RemoveField(
            model_name='main_tray',
            name='layoutobject_ptr',
        ),
        migrations.RemoveField(
            model_name='main_tray',
            name='parent',
        ),
        migrations.DeleteModel(
            name='LayoutObject',
        ),
        migrations.DeleteModel(
            name='main_aisle',
        ),
        migrations.DeleteModel(
            name='main_bay',
        ),
        migrations.DeleteModel(
            name='main_enclosure',
        ),
        migrations.DeleteModel(
            name='main_tray',
        ),
    ]
