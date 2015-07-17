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
                ('id', models.AutoField(
                    auto_created=True, verbose_name='ID', primary_key=True,
                    serialize=False
                )),
                ('root_id', models.IntegerField(null=True, editable=False)),
                ('name', models.CharField(null=True, max_length=100)),
                ('slug', models.SlugField(
                    null=True, max_length=100, unique=True, blank=True
                )),
                ('root_server', models.URLField(
                    null=True, default='http://cityfarm.media.mit.edu'
                )),
                ('ip', models.GenericIPAddressField(
                    null=True, editable=False
                )),
                ('layout', models.SlugField(
                    null=True,
                    choices=[
                        ('aisle', 'aisle'),
                        ('bay', 'bay'),
                        ('tray', 'tray')
                    ]
                )),
            ],
            options={
                'managed': True,
            },
        ),
    ]
