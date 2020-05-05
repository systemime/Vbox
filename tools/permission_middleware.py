from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect, HttpResponse, render

import time
import re


class PermissionAuth(MiddlewareMixin):
    # 白名单
    white_login = [
        reverse('users:login'),
        reverse('users:registered'),
        # '^/hello-tornado*',
        '^/favicon.ico*',
        '^/admin*',
    ]
    # 权限白名单
    white_permission = [
        reverse('users:logout'),
        reverse('get_pod_num'),
        reverse('users:bash_info'),
        '^/media*'
    ]

    def process_request(self, request):
        print("=========================================")
        print(request.path_info)
        print(request.get_full_path())
        print(request.path)
        print("=========================================")
        for req in self.white_login:
            if re.match(req, request.path):
                return
        # 登录认证
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

        # 权限白名单
        for req in self.white_permission:
            if re.match(req, request.path):
                return
        # 权限认证
        permission_list = request.session.get(settings.PERMISSION_SESSION_KEY)
        # print(permission_list)
        # [{'url': '/xxx/'},{'url': '/xxx/(/d+)'}]
        for reg in permission_list:
            reg = r"^%s" % reg['url']
            if re.match(reg, request.path):
                return
        else:  # for...else语句
            return HttpResponse("您无权进行操作")
