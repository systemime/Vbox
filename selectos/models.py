from django.db import models
import time

# Create your models here.


class Systemos(models.Model):

    os_list = (
        (0, 'Ubuntu'),
        (1, 'Centos'),
    )

    language_list = (
        (0, 'Python2'),
        (1, 'Python3'),
        (2, 'java1.8'),
    )

    database_list = (
        (0, 'null'),
        (1, 'mysql5.7'),
        (2, 'Redis'),
        (3, 'MongoDB'),
    )

    proxy_list = (
        (0, 'null'),
        (1, 'nginx'),
        (2, 'tomcat'),
    )
    # 创建时间的md5值
    deployment = models.CharField(unique=True, max_length=64, default='emp_name', choices=os_list, null=False, verbose_name='deployment_name')
    version = models.CharField(max_length=8, null=False, default='apps/v1', verbose_name='容器版本')
    create_time = models.IntegerField(null=False, default=int(time.time()), verbose_name='创建时间戳')

    os = models.CharField(max_length=64, choices=os_list, null=False, verbose_name='操作系统')
    cpus = models.IntegerField(null=False, default=1, verbose_name='cpu个数')
    ram = models.IntegerField(null=False, default=2048, verbose_name='内存容量')
    language = models.CharField(max_length=64, choices=language_list, null=True, blank=True, verbose_name='编程语言')
    database = models.CharField(max_length=64, choices=database_list, null=True, blank=True, verbose_name='数据库')
    proxy = models.CharField(max_length=64, null=True, blank=True, verbose_name='代理')
    is_vnc = models.BooleanField(null=False, default=True, verbose_name='是否需要vnc')  # 默认需要的
    port = models.IntegerField(max_length=5, null=True, blank=True, verbose_name='开放端口')  # 只允许有一个
    use_time = models.IntegerField(max_length=2, null=False, verbose_name='租用时长')  # 最长24小时

    class Meta:
        verbose_name = '用户配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.os_list, self.database_list, self.language_list, self.proxy_list




