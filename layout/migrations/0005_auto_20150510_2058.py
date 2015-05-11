# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0004_auto_20150510_2056'),
    ]

    operations = [
        migrations.CreateModel(
            name='main_aisle',
            fields=[
                ('layoutobject_ptr', models.OneToOneField(to='layout.LayoutObject', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
                ('width', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('x', models.FloatField(null=True)),
                ('y', models.FloatField(null=True)),
                ('z', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('layout.layoutobject', models.Model),
        ),
        migrations.CreateModel(
            name='main_bay',
            fields=[
                ('layoutobject_ptr', models.OneToOneField(to='layout.LayoutObject', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
                ('width', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('x', models.FloatField(null=True)),
                ('y', models.FloatField(null=True)),
                ('z', models.FloatField(null=True)),
                ('parent', models.ForeignKey(to='layout.main_aisle', related_name='children')),
            ],
            options={
                'abstract': False,
            },
            bases=('layout.layoutobject', models.Model),
        ),
        migrations.CreateModel(
            name='main_enclosure',
            fields=[
                ('layoutobject_ptr', models.OneToOneField(to='layout.LayoutObject', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
                ('width', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('layout.layoutobject', models.Model),
        ),
        migrations.CreateModel(
            name='main_tray',
            fields=[
                ('layoutobject_ptr', models.OneToOneField(to='layout.LayoutObject', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
                ('width', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('x', models.FloatField(null=True)),
                ('y', models.FloatField(null=True)),
                ('z', models.FloatField(null=True)),
                ('num_rows', models.IntegerField()),
                ('num_cols', models.IntegerField()),
                ('parent', models.ForeignKey(to='layout.main_bay')),
            ],
            options={
                'abstract': False,
            },
            bases=('layout.layoutobject', models.Model),
        ),
        migrations.AddField(
            model_name='main_aisle',
            name='parent',
            field=models.ForeignKey(to='layout.main_enclosure', default=1, related_name='children'),
        ),
    ]
