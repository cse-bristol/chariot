# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 14:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0006_auto_20170926_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploymentsensor',
            name='last_notification_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
