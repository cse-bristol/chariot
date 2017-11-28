# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import deployments.models
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('deployments', '0013_deployment_7day_schedule_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deployment',
            name='client_notifications_from',
        ),
        migrations.RemoveField(
            model_name='deployment',
            name='client_notifications_to',
        )
    ]
