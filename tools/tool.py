from django.conf import settings
from django.http import JsonResponse
from django.db.models import Sum, Count
from functools import wraps
import hashlib
import time
import random
from django.urls import reverse
from django.shortcuts import redirect
import platform  # platform.system().lower() in ['linux', 'unix']
import os
from Vbox import celery_app
from users import models
from selectos.models import Systemos
from django.core.cache import cache  # 操作缓存 clear() 清空所有缓存


# 用户密码加密
def hash_code(s):
    token = settings.PASSWD_TOKEN
    h = hashlib.sha256()
    s += token
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


# 生成随机字符串
def gen_rand_char(length=16, chars='qwertyuioplkjhgfdsazxcvbnm1236547890PLKMNBVCXZASDFGHJKOIUYTREWQ'):
    return ''.join(random.sample(chars, length))


# 登陆装饰器
def login_required(func):
    @wraps(func)    # 保留原函数信息，重要
    def wrapper(request, *args, **kwargs):
        try:
            if not request.session.get('islogin', None):
                return redirect(reverse('users:login'))
        except Exception:
            return redirect(reverse('users:login'))
        lasttime = int(request.session.get('lasttime'))
        now = int(time.time())
        if now - lasttime > settings.SESSION_COOKIE_AGE:
            return redirect(reverse('users:logout'))
        else:
            request.session['lasttime'] = now
        return func(request, *args, **kwargs)
    return wrapper


# 必须 POST 方式装饰器
def post_required(func):
    @wraps(func)    # 保留原函数信息，重要
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse({"code": 405, "err": "方法不允许"})
        return func(request, *args, **kwargs)
    return wrapper

# deployment name基于时间戳生成，防止重复
def get_deploy_name():
    m = hashlib.md5()
    t = str(time.time())
    m.update(t.encode(encoding='utf-8'))
    deploy_name = m.hexdigest()
    return deploy_name, t


def mkdir(namespace):  # 创建挂载目录
    path = "/home/soul/tools/" + namespace
    if not os.path.exists(path):
        os.makedirs(path)
    return path


@celery_app.task(ignore_result=True)  # 不存储任务状态(无返回的意思?)
def res(res_file, res, enter=True):
    res_file = settings.MEDIA_ROOT + '/' + res_file

    if enter:
        with open(res_file, 'a+') as f:
            for line in res:
                f.write('{}\n'.format(line))
    else:
        with open(res_file, 'a+') as f:
            for line in res:
                f.write('{}'.format(line))


def not_cache(key_pod_num, username):
    """
    写入用户username的虚拟机数量缓存
    :param key_pod_num: 缓存关键字
    :param username: 用户名/namespace
    """
    num = Systemos.objects.filter(namespace=username).count()
    num = 0 if not num else num
    cache.set(key_pod_num, num)


def user_cache():
    """
    获取所有用户名缓存以及资源配合
    """
    # 用户名缓存，注册/登录使用
    users = models.UserProfile.objects.values('username')
    # [{'name': 'xxx'}, {'name': 'xxx'}, {'name': 'xxx'}]
    cache.set('users_name', users)

    # 资源配额，创建/删除使用
    quota = {}
    for user in users:
        if user['username'] != 'soul':
            quota[user['username']] = Systemos.objects.filter(
                namespace__exact=user['username']
            ).aggregate(Sum('cpus'), Sum('ram'), Count('id'))
    # {'systemime': {'cpus__sum': 4, 'ram__sum': 4096, 'id__count': 3},'xxx':{...}}
    cache.set('users_quota', quota)
