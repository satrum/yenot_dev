# Generated by Django 2.0.1 on 2018-04-05 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0062_auto_20180404_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_sources', to=settings.AUTH_USER_MODEL),
        ),
    ]
