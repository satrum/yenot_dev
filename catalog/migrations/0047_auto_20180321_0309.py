# Generated by Django 2.0.1 on 2018-03-21 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0046_auto_20180316_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='link',
            field=models.URLField(default='https://yeenot.today', max_length=100),
        ),
    ]
