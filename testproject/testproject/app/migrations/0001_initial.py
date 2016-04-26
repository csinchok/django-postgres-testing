# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-26 16:24
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foo', models.CharField(max_length=255)),
                ('bar', models.IntegerField()),
                ('baz', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
    ]
