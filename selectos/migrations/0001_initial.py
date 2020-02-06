# Generated by Django 2.2.3 on 2020-02-06 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Systemos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('namespace', models.CharField(default='default', max_length=63, verbose_name='命名空间')),
                ('deployment', models.CharField(choices=[(0, 'Ubuntu'), (1, 'Centos')], default='emp_name', max_length=64, unique=True, verbose_name='deployment_name')),
                ('version', models.CharField(default='apps/v1', max_length=8, verbose_name='容器版本')),
                ('labels', models.CharField(default='username', max_length=63, verbose_name='容器标签')),
                ('create_time', models.CharField(default='0', max_length=63, verbose_name='创建时间戳')),
                ('storage', models.IntegerField(default='5', verbose_name='硬盘容量G')),
                ('os', models.CharField(choices=[(0, 'Ubuntu'), (1, 'Centos')], max_length=64, verbose_name='操作系统')),
                ('cpus', models.IntegerField(default=1, verbose_name='cpu个数')),
                ('ram', models.IntegerField(default=2048, verbose_name='内存容量')),
                ('language', models.CharField(blank=True, choices=[(0, 'Python2'), (1, 'Python3'), (2, 'java1.8')], max_length=64, null=True, verbose_name='编程语言')),
                ('database', models.CharField(blank=True, choices=[(0, 'null'), (1, 'mysql5.7'), (2, 'Redis'), (3, 'MongoDB')], max_length=64, null=True, verbose_name='数据库')),
                ('is_vnc', models.BooleanField(default=True, verbose_name='是否需要vnc')),
                ('port', models.IntegerField(blank=True, null=True, verbose_name='pod开放端口')),
                ('nodeport', models.IntegerField(blank=True, default=0, null=True, verbose_name='service外部端口')),
                ('use_time', models.IntegerField(verbose_name='租用时长')),
            ],
            options={
                'verbose_name': '用户配置',
                'verbose_name_plural': '用户配置',
            },
        ),
    ]
