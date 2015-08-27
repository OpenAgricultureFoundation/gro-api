# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0002_auto_20150819_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farm',
            name='ip',
            field=models.GenericIPAddressField(null=True, editable=False, help_text='The current IP address of this farm'),
        ),
        migrations.AlterField(
            model_name='farm',
            name='layout',
            field=models.SlugField(null=True, choices=[('aisle', 'A collection of aisles'), ('bay', 'A collection of bays'), ('tray', 'A collections of trays')]),
        ),
        migrations.AlterField(
            model_name='farm',
            name='name',
            field=models.CharField(null=True, max_length=100, help_text='Human readable farm name'),
        ),
        migrations.AlterField(
            model_name='farm',
            name='root_server',
            field=models.URLField(default='http://openag.media.mit.edu', null=True, help_text='URL of the root server to which this farm is registered'),
        ),
        migrations.AlterField(
            model_name='farm',
            name='slug',
            field=models.SlugField(null=True, unique=True, blank=True, help_text='Unique farm identifier', max_length=100),
        ),
    ]
