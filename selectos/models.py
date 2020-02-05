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

class TerminalLog(models.Model):
    user = models.CharField(max_length=64, verbose_name='用户')
    depname = models.CharField(max_length=64, verbose_name='DEPLOYMENT')
    ip = models.GenericIPAddressField(verbose_name='PODIP')
    protocol = models.CharField(max_length=64, default='ssh', verbose_name="协议")
    port = models.SmallIntegerField(default=22, verbose_name='端口')
    cmd = models.TextField('命令详情', blank=True, null=True)
    detail = models.CharField(max_length=128, blank=True, null=True, verbose_name="结果详情(文件名)")
    address = models.GenericIPAddressField('IP地址', blank=True, null=True, verbose_name="客户端ip")
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    start_time = models.DateTimeField('会话开始时间')
    create_time = models.DateTimeField('事件时间', auto_now_add=True)

    def __str__(self):
        return self.user

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '在线会话日志'
        verbose_name_plural = '在线会话日志'


class TerminalSession(models.Model):
    PROTOCOL_CHOICES = (
        (1, 'ssh'),
        (2, 'vnc'),
    )

    TYPE_CHOICES = (
        (1, 'webssh'),
        (2, 'webvnc'),
    )

    name = models.CharField(max_length=512, verbose_name='会话名称')
    group = models.CharField(default='chat_default', max_length=512, verbose_name='会话组')
    type = models.SmallIntegerField(default=1, choices=TYPE_CHOICES, verbose_name='类型')
    user = models.CharField(max_length=128, verbose_name='用户')
    host = models.GenericIPAddressField(verbose_name='主机')
    port = models.SmallIntegerField(default=22, verbose_name='端口')
    username = models.CharField(max_length=128, verbose_name='账号')
    protocol = models.SmallIntegerField(default=1, choices=PROTOCOL_CHOICES, verbose_name='协议')
    address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    locked = models.BooleanField(default=False, verbose_name='会话状态')
    create_time = models.DateTimeField('会话时间', auto_now_add=True)

    def __str__(self):
        return '{0}'.format(self.name)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '在线会话'
        verbose_name_plural = '在线会话'


