# Generated by Django 2.0.1 on 2018-02-17 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0032_auto_20180217_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ImageField(upload_to='banner_images/'),
        ),
    ]
