# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0003_auto_20150810_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='site',
            field=models.OneToOneField(editable=False, to='layout.PlantSite', null=True, related_name='plant'),
        ),
    ]
