# Generated by Django 2.0.1 on 2018-02-27 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0042_remove_source_stats_median'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='sourceid',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='catalog.Source'),
        ),
    ]
