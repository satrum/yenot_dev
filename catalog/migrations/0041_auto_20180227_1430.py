# Generated by Django 2.0.1 on 2018-02-27 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0040_auto_20180226_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='stats_avg',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='average rating of news from source', max_digits=10),
        ),
        migrations.AddField(
            model_name='source',
            name='stats_dislikes',
            field=models.IntegerField(blank=True, default=0, help_text='sum of dislikes all news from source'),
        ),
        migrations.AddField(
            model_name='source',
            name='stats_likes',
            field=models.IntegerField(blank=True, default=0, help_text='sum of likes all news from source'),
        ),
        migrations.AddField(
            model_name='source',
            name='stats_max',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='maximum rating of news from source', max_digits=10),
        ),
        migrations.AddField(
            model_name='source',
            name='stats_median',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='median  rating of news from source', max_digits=10),
        ),
        migrations.AddField(
            model_name='source',
            name='stats_min',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='minimum rating of news from source', max_digits=10),
        ),
        migrations.AddField(
            model_name='source',
            name='stats_sum',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='sum of  rating of news from source', max_digits=10),
        ),
        migrations.AlterField(
            model_name='source',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10),
        ),
    ]