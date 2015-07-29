# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('root_id', models.IntegerField(editable=False, null=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('slug', models.SlugField(max_length=100, unique=True, blank=True, null=True)),
                ('root_server', models.URLField(default='http://cityfarm.media.mit.edu', null=True)),
                ('ip', models.GenericIPAddressField(editable=False, null=True)),
                ('layout', models.SlugField(choices=[('aisle', 'Single Aisle'), ('bay', 'Single Bay'), ('tray', 'Single Tray (i.e. GroBot)')], null=True)),
            ],
            options={
                'managed': True,
            },
        ),
    ]
