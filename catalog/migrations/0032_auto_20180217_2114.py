# Generated by Django 2.0.1 on 2018-02-17 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0031_auto_20180217_2111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ImageField(height_field=300, upload_to='banner_images/', width_field=400),
        ),
    ]
