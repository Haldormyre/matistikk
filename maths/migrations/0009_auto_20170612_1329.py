# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-12 11:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0008_auto_20170611_2245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskorder',
            name='task',
        ),
        migrations.AddField(
            model_name='taskorder',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='maths.Item'),
        ),
    ]