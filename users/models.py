from django.db import models
from django.contrib.auth.models import AbstractUser
from rbac.models import Role, Menu
import time


# Create your models here.
class UserProfile(AbstractUser):
    SEX_CHOICES = (
        ('male', '男'),
        ('female', '女')
    )
    nick_name = models.CharField(max_length=20, verbose_name='昵称', null=True, blank=True)
    password = models.CharField(max_length=256, verbose_name='密码')
    avatar = models.ImageField(upload_to='media', default='default.jpg')
    sex = models.CharField(max_length=32, choices=SEX_CHOICES, default="male", verbose_name='性别')
    mobile = models.CharField(max_length=11, verbose_name='手机', null=True, blank=True)
    address = models.CharField(max_length=200, verbose_name='地址', null=True, blank=True)
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    role = models.ManyToManyField(Role, blank=True, verbose_name='用户角色')
    memo = models.TextField(blank=True, null=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')
    pod_num = models.IntegerField(null=False, default=0, verbose_name='容器数量')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __str__(self):
        return self.username


class UserLog(models.Model):
    event_type_choice = (
        (1, '登陆'),
        (2, '退出'),
        (3, '登陆错误'),
        (4, '修改密码失败'),
        (5, '修改密码成功'),
        (6, '新增用户'),
        (7, '删除用户用户'),
        (8, '更新用户信息'),
        (9, '创建虚拟主机'),
        (10, '创建失败'),
        (11, '删除虚拟主机'),
        (12, '建立ssh连接'),
        (13, '关闭ssh连接'),
        (14, '建立vnc连接'),
        (15, '关闭vnc连接'),
        (16, '导出主机数据'),
        (17, '申请子账户'),
        (18, '批准子账户'),
        (19, '访问首页'),
        (20, '访问容器信息'),
        (21, '访问个人页面'),
        (22, '访问文件上传'),
        (23, '上传文件'),
        (24, '访问文件列表'),
        (25, '删除文件'),
    )
    log_type = (
        (0, '系统日志'),
        (1, '一级用户日志'),
        (2, '二级用户日志'),
    )
    # 不产生关联关系，纯记录
    user = models.CharField(max_length=64, blank=True, null=True, verbose_name="用户")  # 为了显示便利存储nickname，查询因采用Q查询，包含role
    role = models.SmallIntegerField(default=0, choices=log_type, verbose_name="日志级别")
    event_type = models.SmallIntegerField('事件类型', choices=event_type_choice, default=1)
    detail = models.TextField('事件详情', default='登陆成功')
    address = models.GenericIPAddressField(verbose_name='IP地址', blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    create_time = models.DateTimeField('事件时间', auto_now_add=True)
    other = models.TextField(verbose_name="系统事件")  # request.header信息或kube处理信息


    def __str__(self):
        return self.get_event_type_display()

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '用户操作日志'  # 管理员暂时放在此处
        verbose_name_plural = '用户操作日志'
