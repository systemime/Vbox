from django.db import models

# Create your models here.


class Papers(models.Model):
    user = models.ForeignKey('users.UserProfile', to_field='username', related_name='file_upload_user', null=False,
                             on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100, null=False, verbose_name='文件名')
    size = models.IntegerField(default=1024, verbose_name='文件大小')
    create_time = models.DateTimeField('上传时间', auto_now_add=True)
