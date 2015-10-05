# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, auto_created=True, verbose_name='ID',
                    serialize=False
                )),
                ('code', models.CharField(max_length=1, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('read_only', models.BooleanField(
                    default=False, editable=False
                )),
                ('resource_count', models.PositiveIntegerField(
                    editable=False, default=0
                )),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceProperty',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, auto_created=True, verbose_name='ID',
                    serialize=False
                )),
                ('code', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=100)),
                ('resource_type', models.ForeignKey(
                    to='resources.ResourceType'
                )),
                ('read_only', models.BooleanField(
                    default=False, editable=False
                )),
                ('sensing_point_count', models.PositiveIntegerField(
                    editable=False, default=0
                )),
            ],
            options={
                'unique_together': set([
                    ('name', 'resource_type'), ('code', 'resource_type')
                ]),
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, serialize=False, verbose_name='ID',
                    primary_key=True
                )),
                ('index', models.PositiveIntegerField(editable=False)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('resource_type', models.ForeignKey(
                    to='resources.ResourceType'
                )),
                ('location_id', models.PositiveIntegerField()),
                ('location_type', models.ForeignKey(
                    to='contenttypes.ContentType'
                )),
            ],
            options={
                'unique_together': set([('index', 'resource_type')]),
            },
        ),
    ]
