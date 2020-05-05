from django.db import models


# Create your models here.
class Menu(models.Model):
    title = models.CharField(max_length=32, verbose_name='菜单标题')

    class Meta:
        verbose_name = "菜单表"
        verbose_name_plural = verbose_name

    # 重写__str__方法，实例化后的对象将以字符串的形式展示，但实际是一个obj,所以，请不要相信你的眼睛，必要时使用type(arg)进行验证
    def __str__(self):
        return self.title


class Permission(models.Model):
    """
        权限表
        可以做二级菜单的权限   menu 关联 菜单表
        不可以做菜单的权限    menu=null
    """
    url = models.URLField(max_length=64)
    title = models.CharField(max_length=64)
    menu = models.ForeignKey("Menu", null=True, blank=True, verbose_name="所属菜单", on_delete=models.CASCADE)

    class Meta:
        verbose_name = '权限表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Role(models.Model):
    rolename = models.CharField(max_length=32, verbose_name="角色名称")
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name='权限配置')
    menu = models.ManyToManyField(Menu, blank=True, verbose_name='菜单列表')

    class Meta:
        verbose_name = '用户角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.rolename
