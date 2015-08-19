# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_auto_20150811_2307'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceEffect',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('code', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'default_related_name': 'effectors',
            },
        ),
        migrations.AlterModelOptions(
            name='resourcetype',
            options={},
        ),
        migrations.AddField(
            model_name='resourceproperty',
            name='read_only',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='resourcetype',
            name='read_only',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='resourceeffect',
            name='resource_type',
            field=models.ForeignKey(to='resources.ResourceType'),
        ),
        migrations.AlterUniqueTogether(
            name='resourceeffect',
            unique_together=set([('code', 'resource_type', 'name', 'resource_type')]),
        ),
    ]
