# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def load_fixture(apps, schema_editor): # pylint: disable=unused-argument
    from django.core.management import call_command
    call_command('loaddata', 'initial_actuators', app_label='actuators', verbosity=0)

def unload_fixture(apps, schema_editor): # pylint: disable=unused-argument
    ActuatorType = apps.get_model("actuators", "ActuatorType")
    ActuatorType.objects.filter(read_only=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('actuators', '0001_initial'), ('resources', '0002_setup'),
        ('control', '0002_setup')
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
