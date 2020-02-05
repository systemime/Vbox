from django.conf import settings
from django.http import JsonResponse
from functools import wraps
import hashlib
import time
import random
from django.urls import reverse
from django.shortcuts import redirect
import platform  # platform.system().lower() in ['linux', 'unix']
import os
from Vbox import celery_app


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

try:
    session_exipry_time = settings.CUSTOM_SESSION_EXIPRY_TIME
except Exception:
    session_exipry_time = 60 * 30


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
        if now - lasttime > session_exipry_time:
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


