# Generated by Django 2.0.1 on 2018-03-30 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0052_auto_20180329_0335'),
    ]

    operations = [
        migrations.CreateModel(
            name='YeenotSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('num_value', models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='digital value of settings', max_digits=10)),
            ],
        ),
    ]
