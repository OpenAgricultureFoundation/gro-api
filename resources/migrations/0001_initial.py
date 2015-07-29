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
        ('layout', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('location', models.ForeignKey(related_name='resources', to='layout.LayoutObject')),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResourceProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('read_only', models.BooleanField(editable=False, default=False)),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('read_only', models.BooleanField(editable=False, default=False)),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='resourceproperty',
            name='resource_type',
            field=models.ForeignKey(related_name='properties', to='resources.ResourceType'),
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_type',
            field=models.ForeignKey(related_name='resources', to='resources.ResourceType'),
        ),
        migrations.RunPython(
            load_fixture, reverse_code=unload_fixture
        ),
    ]
