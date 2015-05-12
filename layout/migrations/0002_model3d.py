# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Model3D',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('file', models.FileField(upload_to='')),
                ('width', models.FloatField()),
                ('length', models.FloatField()),
                ('height', models.FloatField()),
            ],
        ),
    ]
