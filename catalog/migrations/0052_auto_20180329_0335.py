# Generated by Django 2.0.1 on 2018-03-29 00:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0051_uservotes_vote_rate_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='text',
            field=models.TextField(help_text='description of news', max_length=1000, validators=[django.core.validators.MinLengthValidator(20)]),
        ),
    ]
