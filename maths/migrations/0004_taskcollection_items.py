# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-09 06:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0003_auto_20170608_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskcollection',
            name='items',
            field=models.ManyToManyField(to='maths.Item'),
        ),
    ]