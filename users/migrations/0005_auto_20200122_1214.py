# Generated by Django 2.2.3 on 2020-01-22 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200122_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default='/media/default.jpg', upload_to='media'),
        ),
    ]