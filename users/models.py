from django.db import models
from django.contrib.auth.models import AbstractUser
import time


# Create your models here.
class UserProfile(AbstractUser):
    SEX_CHOICES = (
        ('male', '男'),
        ('female', '女')
    )
    ROLE_CHOICES = (
        (0, '超级管理员'),
        (1, '一级用户'),
        (2, '二级用户')
    )
    nick_name = models.CharField(max_length=20, verbose_name='昵称', null=True, blank=True)
    password = models.CharField(max_length=256, verbose_name='密码')
    avatar = models.ImageField(upload_to='media', default='default.jpg')
    sex = models.CharField(max_length=32, choices=SEX_CHOICES, default="male", verbose_name='性别')
    mobile = models.CharField(max_length=11, verbose_name='手机', null=True, blank=True)
    address = models.CharField(max_length=200, verbose_name='地址', null=True, blank=True)
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    role = models.SmallIntegerField(default=1, choices=ROLE_CHOICES, verbose_name='用户级别')
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