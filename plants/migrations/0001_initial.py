# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layout', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('sown_date', models.DateTimeField()),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlantType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('common_name', models.CharField(max_length=100)),
                ('latin_name', models.CharField(max_length=100)),
                ('plant_size', models.CharField(choices=[('short-leafy', 'Short Leafy'), ('short-branchy', 'Short Branchy'), ('medium-leafy', 'Medium Leafy'), ('medium-branchy', 'Medium Branchy'), ('tall-leafy', 'Tall Leafy'), ('tall-branchy', 'Tall Barnchy')], max_length=100)),
            ],
            options={
                'managed': True,
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='plant',
            name='plant_type',
            field=models.ForeignKey(related_name='plants', to='plants.PlantType'),
        ),
        migrations.AddField(
            model_name='plant',
            name='site',
            field=models.OneToOneField(to='layout.PlantSite', related_name='plant'),
        ),
    ]
