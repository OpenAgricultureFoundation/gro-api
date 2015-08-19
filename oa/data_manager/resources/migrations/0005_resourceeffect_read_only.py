# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0004_auto_20150818_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourceeffect',
            name='read_only',
            field=models.BooleanField(editable=False, default=False),
        ),
    ]
