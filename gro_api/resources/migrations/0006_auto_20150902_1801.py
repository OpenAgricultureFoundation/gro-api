# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0005_resourceeffect_read_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourceproperty',
            name='units',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='resourceeffect',
            unique_together=set([('name', 'resource_type'), ('code', 'resource_type')]),
        ),
    ]
