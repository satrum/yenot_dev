# Generated by Django 2.0.1 on 2018-02-21 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0035_auto_20180219_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='place',
            field=models.CharField(blank=True, choices=[('t', 'Top horizontal'), ('l', 'Under Top on Left'), ('r', 'Under Top on Right')], default='t', help_text='Banner place on site', max_length=1),
        ),
    ]