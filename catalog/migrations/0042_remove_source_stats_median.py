# Generated by Django 2.0.1 on 2018-02-27 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0041_auto_20180227_1430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='source',
            name='stats_median',
        ),
    ]
