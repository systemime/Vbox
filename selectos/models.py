from django.db import models
import time
from users.models import UserProfile

# Create your models here.


class Systemos(models.Model):
    """
    any user，one namespace，one service，limit three deployment（pod）
    username = namespace-name = service-name = pod-label
    deployment-name = create-time md5
    port in pod
    node_port is 80
    与用户表 OneToMany 关系
    """

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

    user = models.ForeignKey('users.UserProfile', to_field='username', related_name='dep_user', null=False, on_delete=models.CASCADE)
    namespace = models.CharField(max_length=63, null=False, default='default', verbose_name='命名空间')
    deployment = models.CharField(unique=True, max_length=64, default='emp_name', choices=os_list, null=False,
                                  verbose_name='deployment_name')
    version = models.CharField(max_length=8, null=False, default='apps/v1', verbose_name='容器版本')
    labels = models.CharField(max_length=63, null=False, default='username', verbose_name='容器标签')
    create_time = models.CharField(max_length=63, null=False, default='0', verbose_name='创建时间戳')
    storage = models.IntegerField(null=False, default='5', verbose_name='硬盘容量G')

    os = models.CharField(max_length=64, choices=os_list, null=False, verbose_name='操作系统')
    cpus = models.IntegerField(null=False, default=1, verbose_name='cpu个数')
    ram = models.IntegerField(null=False, default=2048, verbose_name='内存容量')
    language = models.CharField(max_length=64, choices=language_list, null=True, blank=True, verbose_name='编程语言')
    database = models.CharField(max_length=64, choices=database_list, null=True, blank=True, verbose_name='数据库')
    is_vnc = models.BooleanField(null=False, default=True, verbose_name='是否需要vnc')  # 默认需要的
    port = models.IntegerField(null=True, blank=True, verbose_name='pod开放端口')  # 只允许有一个
    nodeport = models.IntegerField(null=True, blank=True, default=0, verbose_name='service外部端口')
    use_time = models.IntegerField(null=False, verbose_name='租用时长')  # 最长24小时

    class Meta:
        verbose_name = '用户配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.deployment)




