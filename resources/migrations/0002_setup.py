# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', 'initial_resources', verbosity=0, app_label='resources')

def unload_fixture(apps, schema_editor):
    ResourceType = apps.get_model("resources", "ResourceType")
    ResourceType.objects.filter(read_only=True).delete()
    ResourceProperty = apps.get_model("resources", "ResourceProperty")
    ResourceProperty.objects.filter(read_only=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'), ('control', '0002_setup')
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
