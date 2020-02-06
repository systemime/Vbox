from django.db import models
from users.models import UserProfile

# Create your models here.


class Logs_to_SSH(models.Model):
    user = models.ForeignKey('users.UserProfile', to_field='username', related_name='web_user', null=False,
                             on_delete=models.DO_NOTHING)
    pod_name = models.CharField(max_length=64, default='', null=False, verbose_name='容器名称')
    command = models.CharField(max_length=128, default='', null=True, blank=True, verbose_name='操作命令')
    create_time = models.DateTimeField('事件时间', auto_now_add=True)

    def __str__(self):
        return self.dep_name

    class Meta:
        ordering = ["-create_time"]
        verbose_name = 'webssh终端日志'
        verbose_name_plural = verbose_name



