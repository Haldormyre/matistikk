# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-08 13:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0037_directory_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='directory',
            name='tasks',
        ),
        migrations.AddField(
            model_name='task',
            name='directory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='maths.Directory'),
            preserve_default=False,
        ),
    ]
