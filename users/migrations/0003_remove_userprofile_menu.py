# Generated by Django 2.2.3 on 2020-04-22 23:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile_menu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='menu',
        ),
    ]
