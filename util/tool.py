from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from functools import wraps
import hashlib
import time
import random
#from webssh.models import TerminalLog
#from user.models import LoginLog
# from tasks.tasks import task_save_res
import platform
import glob
import os


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
                return redirect(reverse('user:login'))
        except Exception:
            return redirect(reverse('user:login'))
        lasttime = int(request.session.get('lasttime'))
        now = int(time.time())
        if now - lasttime > session_exipry_time:
            return redirect(reverse('user:logout'))
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


# 用户密码加密
def hash_code(s):
    token = settings.PASSWD_TOKEN
    h = hashlib.sha256()
    s += token
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


# 生成随机字符串
def gen_rand_char(length=16, chars='0123456789zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA'):
    return ''.join(random.sample(chars, length))



def res(res_file, res, enter=True):
    res_file = settings.MEDIA_ROOT + '/' + res_file
    if platform.system().lower() in ['linux', 'unix']:
        pass
        # task_save_res.delay(res_file, res, enter)
    else:
        if enter:
            with open(res_file, 'a+') as f:
                for line in res:
                    f.write('{}\n'.format(line))
        else:
            with open(res_file, 'a+') as f:
                for line in res:
                    f.write('{}'.format(line))

def file_combine(file_size, file_count, file_path, file_name, file_name_md5):
    """
    使用fileinput分段上传过来的数据
    验证分段数量和分段总大小正确后才合并
    """
    try:
        file_lists = glob.glob(r'{}/{}_{}_*'.format(file_path, file_name_md5, file_count))
        if len(file_lists) != file_count:
            return False
        else:
            total_size = 0
            for file in file_lists:
                total_size += os.path.getsize(file)
            if total_size == file_size:
                with open('{}/{}'.format(file_path, file_name), 'wb') as f:
                    for i in range(1, file_count + 1):
                        with open('{}/{}_{}_{}'.format(file_path, file_name_md5, file_count, i), 'rb') as chunk:
                            f.write(chunk.read())
                        os.remove('{}/{}_{}_{}'.format(file_path, file_name_md5, file_count, i))
                return True
            else:
                return False
    except Exception:
        return False


def convert_byte(byte):
    byte = int(byte)
    if byte <= 1024:
        return '{} B'.format(byte)
    elif 1024 < byte <= 1048576:
        return '{} KB'.format('%.2f' % (byte / 1024))
    elif 1048576 < byte <= 1073741824:
        return '{} MB'.format('%.2f' % (byte / 1024 / 1024))
    elif 1073741824 < byte <= 1099511627776:
        return '{} GB'.format('%.2f' % (byte / 1024 / 1024 / 1024))
    elif byte > 1099511627776:
        return '{} TB'.format('%.2f' % (byte / 1024 / 1024 / 1024 / 1024))
