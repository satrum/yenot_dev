# Generated by Django 2.0.1 on 2018-02-26 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0039_auto_20180226_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coin',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
