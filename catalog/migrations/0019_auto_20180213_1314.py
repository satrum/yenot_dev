# Generated by Django 2.0.1 on 2018-02-13 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0018_auto_20180213_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='proof_image',
            field=models.ImageField(blank=True, upload_to='image_news/'),
        ),
    ]