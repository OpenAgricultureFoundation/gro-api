# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20150810_1824'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reciperun',
            options={'get_latest_by': 'start_timestamp'},
        ),
    ]
