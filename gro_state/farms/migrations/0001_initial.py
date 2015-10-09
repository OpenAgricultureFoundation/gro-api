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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Human readable farm name', null=True, max_length=100)),
                ('slug', models.SlugField(help_text='Unique farm identifier', null=True, max_length=100)),
                ('layout', models.SlugField(null=True, choices=[('aisle', 'A collection of aisles'), ('bay', 'A collection of bays'), ('tray', 'A collections of trays')])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
