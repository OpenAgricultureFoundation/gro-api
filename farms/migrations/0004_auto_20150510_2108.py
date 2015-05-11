# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0003_auto_20150510_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farm',
            name='layout',
            field=models.SlugField(choices=[('grobot', 'grobot'), ('main', 'main system')]),
        ),
    ]
