# Generated by Django 2.0.1 on 2018-04-16 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0068_auto_20180415_0450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promo_task',
            name='param',
            field=models.CharField(choices=[('d', 'Day'), ('w', 'Week'), ('m', 'Month')], default='w', help_text='Parameters of promo task', max_length=1),
        ),
        migrations.AlterField(
            model_name='yeenotsettings',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]