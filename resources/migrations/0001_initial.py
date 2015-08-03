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
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('location_id', models.PositiveIntegerField()),
                ('location_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceProperty',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('code', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=100)),
                ('read_only', models.BooleanField(default=False, editable=False)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('read_only', models.BooleanField(default=False, editable=False)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='resourceproperty',
            name='resource_type',
            field=models.ForeignKey(to='resources.ResourceType', related_name='properties'),
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_type',
            field=models.ForeignKey(to='resources.ResourceType', related_name='resources'),
        ),
    ]
