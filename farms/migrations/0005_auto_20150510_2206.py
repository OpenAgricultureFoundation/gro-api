# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0004_auto_20150510_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farm',
            name='layout',
            field=models.SlugField(choices=[('main', 'main system'), ('grobot', 'grobot')]),
        ),
    ]
