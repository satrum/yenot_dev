# Generated by Django 2.0.1 on 2018-04-03 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0059_auto_20180403_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='link',
            field=models.URLField(default='https://yeenot.today', max_length=100, verbose_name='REFERENCE ON NEWS:'),
        ),
    ]
