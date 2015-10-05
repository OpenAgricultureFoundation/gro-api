# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0003_actuatortype_read_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlprofile',
            name='read_only',
            field=models.BooleanField(editable=False, default=False),
        ),
        migrations.AlterUniqueTogether(
            name='controlprofile',
            unique_together=set([('name', 'actuator_type')]),
        ),
    ]
