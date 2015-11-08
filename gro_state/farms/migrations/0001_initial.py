# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Human readable farm name', null=True, max_length=100)),
                ('slug', models.SlugField(help_text='Unique farm identifier', null=True, max_length=100)),
                ('layout', models.SlugField(help_text='Layout schema to use', null=True, choices=[('aisle', 'A collection of aisles'), ('bay', 'A collection of bays'), ('general', 'Arbitrary tree of nodes'), ('tray', 'A collections of trays')])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
