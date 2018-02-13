# Generated by Django 2.0.1 on 2018-01-26 09:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20180126_0249'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='link',
            field=models.URLField(default='https://enot.channel', max_length=100),
        ),
        migrations.AddField(
            model_name='news',
            name='moderation_status',
            field=models.CharField(blank=True, choices=[('a', 'Added and sended for moderate'), ('p', 'Approved for view'), ('d', 'Deleted from view')], default='a', help_text='Moderation status of news', max_length=1),
        ),
        migrations.AddField(
            model_name='news',
            name='promo_status',
            field=models.CharField(blank=True, choices=[('n', 'No promo'), ('y', 'Promoted')], default='n', help_text='Moderation status of news', max_length=1),
        ),
        migrations.AddField(
            model_name='news',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='news',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]