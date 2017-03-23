# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-23 12:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False, verbose_name='Identifier')),
                ('units', models.CharField(max_length=10, verbose_name='Units of Measurement')),
                ('name', models.CharField(max_length=256, verbose_name='Name')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hidden')),
                ('aggregation', models.CharField(default='2m', max_length=10, verbose_name='Aggregation')),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False, verbose_name='Identifier')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('sensor_type', models.CharField(max_length=30, verbose_name='Sensor Type')),
                ('default', models.BooleanField(default=False, verbose_name='Add to New Deployments')),
                ('channels', models.ManyToManyField(to='sensors.Channel')),
                ('cost_channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='sensors.Channel')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
