# Generated by Django 2.2.3 on 2020-02-07 17:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Logs_to_SSH',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pod_name', models.CharField(default='', max_length=64, verbose_name='容器名称')),
                ('command', models.CharField(blank=True, default='', max_length=128, null=True, verbose_name='操作命令')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='事件时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='web_user', to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'verbose_name': 'webssh终端日志',
                'verbose_name_plural': 'webssh终端日志',
                'ordering': ['-create_time'],
            },
        ),
    ]
