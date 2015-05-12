# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='grobot_layout_object',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='grobot_enclosure',
            fields=[
                ('grobot_layout_object_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, to='layout.grobot_layout_object', parent_link=True)),
                ('width', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('layout.grobot_layout_object', models.Model),
        ),
        migrations.CreateModel(
            name='grobot_tray',
            fields=[
                ('grobot_layout_object_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, to='layout.grobot_layout_object', parent_link=True)),
                ('width', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('x', models.FloatField(null=True)),
                ('y', models.FloatField(null=True)),
                ('z', models.FloatField(null=True)),
                ('num_rows', models.IntegerField(null=True)),
                ('num_cols', models.IntegerField(null=True)),
                ('parent', models.ForeignKey(related_name='children', default=1, to='layout.grobot_enclosure')),
            ],
            options={
                'abstract': False,
            },
            bases=('layout.grobot_layout_object', models.Model),
        ),
    ]
