# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import time

import deployments.models
from django.db import migrations, models
import django.db.models.deletion

def migrate_schedule(apps, schema_editor):
    """
    For existing deployments, use their existing schedule for all the days.
    """
    Deployment = apps.get_model('deployments', 'Deployment')
    for deployment in Deployment.objects.all():
        ## New semantics here:
        ## Previously, a blank field meant always send alerts.
        ## Now, it means don't send.
        always_on = (deployment.client_notifications_from is None or deployment.client_notifications_to is None)

        for day_of_week in range(7):
            day = deployment.alert_schedule_days.create(day_of_week=day_of_week,
                                                        client_notifications_from_1=time.min if always_on else deployment.client_notifications_from,
                                                        client_notifications_to_1=time.max if always_on else deployment.client_notifications_to)
            day.save()


class Migration(migrations.Migration):
    dependencies = [
        ('deployments', '0012_deployment_7day_schedule'),
    ]

    operations = [
        migrations.RunPython(migrate_schedule)
    ]
