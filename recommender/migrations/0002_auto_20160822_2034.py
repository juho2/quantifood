# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-22 18:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='food',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='food',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]