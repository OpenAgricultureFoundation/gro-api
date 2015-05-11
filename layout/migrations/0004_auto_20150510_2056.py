# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0003_auto_20150510_1926'),
    ]

    operations = [
        migrations.CreateModel(
            name='LayoutObject',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='main_aisle',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='main_bay',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='main_tray',
            name='parent',
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
