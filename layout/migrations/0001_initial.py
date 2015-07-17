# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LayoutObject',
            fields=[
                ('super_id', models.AutoField(
                    primary_key=True, serialize=False
                )),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Model3D',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, verbose_name='ID', primary_key=True,
                    serialize=False
                )),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='3D_models')),
                ('width', models.FloatField()),
                ('length', models.FloatField()),
                ('height', models.FloatField()),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlantSite',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, verbose_name='ID', primary_key=True,
                    serialize=False
                )),
                ('row', models.IntegerField()),
                ('col', models.IntegerField()),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlantSiteLayout',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, verbose_name='ID', primary_key=True,
                    serialize=False
                )),
                ('row', models.IntegerField()),
                ('col', models.IntegerField()),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TrayLayout',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, verbose_name='ID', primary_key=True,
                    serialize=False
                )),
                ('name', models.CharField(max_length=100)),
                ('num_rows', models.IntegerField()),
                ('num_cols', models.IntegerField()),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Enclosure',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('x', models.FloatField(default=0)),
                ('y', models.FloatField(default=0)),
                ('z', models.FloatField(default=0)),
                ('length', models.FloatField(default=0)),
                ('width', models.FloatField(default=0)),
                ('height', models.FloatField(default=0)),
                ('layout_object', models.OneToOneField(
                    parent_link=True, to='layout.LayoutObject', editable=False
                )),
                ('model', models.ForeignKey(
                    null=True, to='layout.Model3D', related_name='+'
                )),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
            bases=('layout.layoutobject', models.Model),
        ),
        migrations.CreateModel(
            name='Tray',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('x', models.FloatField(default=0)),
                ('y', models.FloatField(default=0)),
                ('z', models.FloatField(default=0)),
                ('length', models.FloatField(default=0)),
                ('width', models.FloatField(default=0)),
                ('height', models.FloatField(default=0)),
                ('num_rows', models.IntegerField(editable=False, default=0)),
                ('num_cols', models.IntegerField(editable=False, default=0)),
                ('parent', models.PositiveIntegerField(db_column='parent_id')),
                ('layout_object', models.OneToOneField(
                    parent_link=True, to='layout.LayoutObject', editable=False
                )),
                ('model', models.ForeignKey(
                    null=True, to='layout.Model3D', related_name='+'
                )),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
            bases=('layout.layoutobject',),
        ),
        migrations.AddField(
            model_name='plantsitelayout',
            name='parent',
            field=models.ForeignKey(
                related_name='plant_sites', to='layout.TrayLayout'
            ),
        ),
        migrations.AddField(
            model_name='plantsite',
            name='parent',
            field=models.ForeignKey(
                related_name='plant_sites', to='layout.Tray'
            ),
        ),
    ]
