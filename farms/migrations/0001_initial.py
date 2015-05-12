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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('farm_id', models.IntegerField(null=True)),
                ('root_server', models.URLField(default='http://cityfarm.media.mit.edu')),
                ('name', models.CharField(max_length=100)),
                ('subdomain', models.SlugField(null=True)),
                ('layout', models.SlugField(choices=[('grobot', 'grobot'), ('main', 'main system')])),
                ('ip', models.GenericIPAddressField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
