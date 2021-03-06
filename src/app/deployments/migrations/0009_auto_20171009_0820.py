# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-09 08:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0008_auto_20171005_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='deployment',
            name='client_notifications_from',
            field=models.TimeField(blank=True, help_text='If left blank notifications will be sent when they are generated', null=True),
        ),
        migrations.AddField(
            model_name='deployment',
            name='client_notifications_to',
            field=models.TimeField(blank=True, help_text='If left blank notifications will be sent when they are generated', null=True),
        ),
    ]
