# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-05 12:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0003_auto_20170905_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='deployment',
            name='prediction',
            field=models.TextField(blank=True, null=True),
        ),
    ]
