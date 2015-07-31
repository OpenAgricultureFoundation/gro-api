# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', 'initial_resources', app_label='resources')

def unload_fixture(apps, schema_editor):
    ResourceType = apps.get_model("resources", "ResourceType")
    ResourceType.objects.filter(read_only=True).delete()
    ResourceProperty = apps.get_model("resources", "ResourceProperty")
    ResourceProperty.objects.filter(read_only=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0002_generate_dynamic_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('location', models.ForeignKey(to='layout.LayoutObject', related_name='resources')),
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
        migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
