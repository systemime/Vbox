# Generated by Django 2.2.3 on 2020-01-30 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='pod_num',
            field=models.IntegerField(default=0, verbose_name='容器数量'),
        ),
    ]