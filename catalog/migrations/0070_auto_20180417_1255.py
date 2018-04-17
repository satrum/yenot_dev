# Generated by Django 2.0.1 on 2018-04-17 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0069_auto_20180416_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promo_task',
            name='type',
            field=models.CharField(blank=True, choices=[('n', 'News promo'), ('s', 'Source promo'), ('b', 'Banner promo')], default='n', help_text='Type of promo task', max_length=1),
        ),
    ]