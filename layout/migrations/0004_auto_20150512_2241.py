# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0003_auto_20150512_2208'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grobot_enclosure',
            name='grobot_layout_object_ptr',
        ),
        migrations.RemoveField(
            model_name='grobot_enclosure',
            name='model',
        ),
        migrations.RemoveField(
            model_name='grobot_tray',
            name='grobot_layout_object_ptr',
        ),
        migrations.RemoveField(
            model_name='grobot_tray',
            name='model',
        ),
        migrations.RemoveField(
            model_name='grobot_tray',
            name='parent',
        ),
        migrations.AlterField(
            model_name='model3d',
            name='file',
            field=models.FileField(upload_to='3D_models'),
        ),
        migrations.DeleteModel(
            name='grobot_enclosure',
        ),
        migrations.DeleteModel(
            name='grobot_layout_object',
        ),
        migrations.DeleteModel(
            name='grobot_tray',
        ),
    ]
