# Generated by Django 2.0.1 on 2018-02-13 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0020_auto_20180213_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='proof_image',
            field=models.ImageField(blank=True, upload_to='catalog/images/'),
        ),
    ]