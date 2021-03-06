# Generated by Django 2.0.1 on 2018-04-14 20:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0066_auto_20180407_2325'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promo_task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, choices=[('n', 'News promo'), ('s', 'Source promo'), ('b', 'Banner promo')], default='n', help_text='Type of promo task', max_length=1)),
                ('status', models.CharField(blank=True, choices=[('o', 'Ordered'), ('p', 'Paid'), ('l', 'Launched'), ('c', 'Completed')], default='o', help_text='Status of promo task', max_length=1)),
                ('param', models.CharField(blank=True, choices=[('w', 'Week'), ('m', 'Month')], default='w', help_text='Parameters of promo task', max_length=1)),
                ('price', models.DecimalField(decimal_places=2, help_text='price of promo task calculated after promo added', max_digits=20)),
                ('time', models.DateTimeField(default=django.utils.timezone.now, help_text='time after promo task added')),
                ('bannerid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Banner', verbose_name='BANNER')),
                ('newsid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.News', verbose_name='NEWS')),
                ('sourceid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Source', verbose_name='SOURCE')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_promo', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
