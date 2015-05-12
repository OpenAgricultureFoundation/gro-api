# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0002_model3d'),
    ]

    operations = [
        migrations.AddField(
            model_name='grobot_enclosure',
            name='model',
            field=models.ForeignKey(null=True, to='layout.Model3D'),
        ),
        migrations.AddField(
            model_name='grobot_tray',
            name='model',
            field=models.ForeignKey(null=True, to='layout.Model3D'),
        ),
        migrations.AddField(
            model_name='model3d',
            name='name',
            field=models.CharField(default='test', max_length=100),
            preserve_default=False,
        ),
    ]
