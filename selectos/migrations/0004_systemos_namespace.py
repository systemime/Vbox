# Generated by Django 2.2.3 on 2020-01-30 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selectos', '0003_auto_20200130_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemos',
            name='namespace',
            field=models.CharField(default='default', max_length=63, verbose_name='命名空间'),
        ),
    ]