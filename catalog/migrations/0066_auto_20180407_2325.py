# Generated by Django 2.0.1 on 2018-04-07 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0065_auto_20180407_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='point',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='user points', max_digits=10),
        ),
        migrations.AddField(
            model_name='profile',
            name='rank',
            field=models.IntegerField(blank=True, default=0, help_text='place of user sorted by points'),
        ),
        migrations.AddField(
            model_name='profile',
            name='sum_right',
            field=models.IntegerField(blank=True, default=0, help_text='right votes (vote_rate>0)'),
        ),
    ]
