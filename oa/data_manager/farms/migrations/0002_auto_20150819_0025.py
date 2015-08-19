# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='farm',
            options={},
        ),
        migrations.AlterField(
            model_name='farm',
            name='root_server',
            field=models.URLField(null=True, default='http://openag.media.mit.edu'),
        ),
    ]
