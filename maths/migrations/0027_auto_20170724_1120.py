# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-24 09:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maths', '0026_auto_20170719_1003'),
    ]

    operations = [
        migrations.CreateModel(
            name='InputFieldTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='answer',
            name='reasoning',
            field=models.CharField(max_length=20000, null=True),
        ),
        migrations.AlterField(
            model_name='answer',
            name='text',
            field=models.CharField(max_length=20000, null=True),
        ),
        migrations.AlterField(
            model_name='geogebraanswer',
            name='base64',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='task',
            name='text',
            field=models.TextField(blank=True, max_length=20000),
        ),
        migrations.AddField(
            model_name='inputfieldtask',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maths.Task'),
        ),
    ]
