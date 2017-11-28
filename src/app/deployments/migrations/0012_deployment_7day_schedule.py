# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import deployments.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0011_deploymentsensor_notifications_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertScheduleDay',

            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(null=False)),
                ('deployment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alert_schedule_days', to='deployments.Deployment')),
                ('client_notifications_from_1', models.TimeField(blank=True, help_text='If left blank, no recording will happen during this period', null=True)),
                ('client_notifications_to_1', models.TimeField(blank=True, help_text='If left blank, no recording will happen during this period', null=True)),
                ('client_notifications_from_2', models.TimeField(blank=True, help_text='If left blank, no recording will happen during this period', null=True)),
                ('client_notifications_to_2', models.TimeField(blank=True, help_text='If left blank, no recording will happen during this period', null=True)),
                ('client_notifications_from_3', models.TimeField(blank=True, help_text='If left blank, no recording will happen during this period', null=True)),
                ('client_notifications_to_3', models.TimeField(blank=True, help_text='If left blank, no recording will happen during this period', null=True))
            ]
        )
    ]
