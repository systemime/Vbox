# Generated by Django 2.2.3 on 2020-02-07 17:24

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(blank=True, max_length=64, null=True, verbose_name='用户')),
                ('role', models.SmallIntegerField(choices=[(0, '系统日志'), (1, '一级用户日志'), (2, '二级用户日志')], default=0, verbose_name='日志级别')),
                ('event_type', models.SmallIntegerField(choices=[(1, '登陆'), (2, '退出'), (3, '登陆错误'), (4, '修改密码失败'), (5, '修改密码成功'), (6, '新增用户'), (7, '删除用户用户'), (8, '更新用户信息'), (9, '创建虚拟主机'), (10, '创建失败'), (11, '删除虚拟主机'), (12, '建立ssh连接'), (13, '关闭ssh连接'), (14, '建立vnc连接'), (15, '关闭vnc连接'), (16, '导出主机数据'), (17, '申请子账户'), (18, '批准子账户'), (19, '访问首页'), (20, '访问容器信息'), (21, '访问个人页面'), (22, '访问文件上传'), (23, '上传文件'), (24, '访问文件列表'), (25, '删除文件')], default=1, verbose_name='事件类型')),
                ('detail', models.TextField(default='登陆成功', verbose_name='事件详情')),
                ('address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('useragent', models.CharField(blank=True, max_length=512, null=True, verbose_name='User_Agent')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='事件时间')),
                ('other', models.TextField(verbose_name='系统事件')),
            ],
            options={
                'verbose_name': '用户操作日志',
                'verbose_name_plural': '用户操作日志',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('nick_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='昵称')),
                ('password', models.CharField(max_length=256, verbose_name='密码')),
                ('avatar', models.ImageField(default='default.jpg', upload_to='media')),
                ('sex', models.CharField(choices=[('male', '男'), ('female', '女')], default='male', max_length=32, verbose_name='性别')),
                ('mobile', models.CharField(blank=True, max_length=11, null=True, verbose_name='手机')),
                ('address', models.CharField(blank=True, max_length=200, null=True, verbose_name='地址')),
                ('enabled', models.BooleanField(default=True, verbose_name='是否启用')),
                ('role', models.SmallIntegerField(choices=[(0, '超级管理员'), (1, '一级用户'), (2, '二级用户')], default=1, verbose_name='用户级别')),
                ('memo', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('last_login_time', models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')),
                ('pod_num', models.IntegerField(default=0, verbose_name='容器数量')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户信息',
                'verbose_name_plural': '用户信息',
                'ordering': ['-create_time'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
