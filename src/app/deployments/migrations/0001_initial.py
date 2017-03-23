# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-23 12:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sensors', '0002_load_initial_data'),
        ('hubs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=255)),
                ('address_line_one', models.CharField(max_length=255)),
                ('post_code', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='deployment_photos', verbose_name='Header Image')),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('hub', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hubs.Hub')),
            ],
        ),
        migrations.CreateModel(
            name='DeploymentAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('layer', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('deployment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deployments.Deployment')),
            ],
            options={
                'verbose_name_plural': 'Deployment Annotations',
            },
        ),
        migrations.CreateModel(
            name='DeploymentSensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost', models.FloatField(default=0)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('deployment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='deployments.Deployment')),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensors.Sensor')),
            ],
            options={
                'verbose_name_plural': 'Deployment Sensors',
                'ordering': ['sensor'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='deploymentsensor',
            unique_together=set([('deployment', 'sensor')]),
        ),
    ]
