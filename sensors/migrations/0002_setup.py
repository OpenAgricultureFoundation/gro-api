# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', 'initial_sensors', app_label='sensors', verbosity=0)

def unload_fixture(apps, schema_editor):
    SensorType = apps.get_model("sensors", "SensorType")
    SensorType.objects.filter(read_only=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0001_initial'), ('control', '0002_setup')
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
