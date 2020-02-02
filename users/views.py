import datetime

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View

# from django.contrib.auth.decorators import login_required
# 用自定义的
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.generic import View
import json, time
import django.utils.timezone as timezone

from tools.k8s import KubeApi
from tools.tool import login_required, hash_code, mkdir

from Vbox import celery_app

from .models import UserProfile
from .forms import ProfileForm
from .forms import LoginForm


@celery_app.task
def create_this_namespace(name):
    task = KubeApi(name)
    info = task.create_user_namespace()
    print(info)

# Create your views here.
# @ratelimit(key=key, rate=rate, method=ALL, block=True)
def login(request):
    # session中存在islogin则显示首页，否则加载登录页面
    if request.session.get('islogin', None):  # 不允许重复登录
        return redirect(reverse('select'))
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        error_message = '请检查填写的内容!'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = UserProfile.objects.get(username=username)
                if not user.enabled:
                    error_message = '用户已禁用!'
                    # event_log(user, 3, '用户 [{}] 已禁用'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                    return render(request, 'login.html', locals())
            except Exception:
                error_message = '用户不存在!'
                # event_log(None, 3, '用户 [{}] 不存在'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return render(request, 'login.html', locals())
            # if user.password == password:
            if user.password == hash_code(password):
                data = {'last_login_time': timezone.now()}  # 获取最后登录时间
                UserProfile.objects.filter(username=username).update(**data)  # 更新数据库内记录
                request.session.set_expiry(0)  # 设置session验证超时时间，关闭浏览器即刻失效
                request.session['issuperuser'] = False  # 默认非超级管理员
                if user.role == 1:      # 超级管理员
                    request.session['issuperuser'] = True
                request.session['islogin'] = True  # 确认登录状态
                request.session['userid'] = user.id  # 获取id
                request.session['username'] = user.username  # 用户名/namespace
                request.session['nickname'] = user.nick_name  # 名称
                request.session['role'] = [v for key, v in UserProfile.ROLE_CHOICES if key==user.role][0]  # 用户级别
                request.session['locked'] = False   # 锁定屏幕
                now = int(time.time())
                request.session['logintime'] = now  # 登录时间
                request.session['lasttime'] = now  # 最后登录时间
                # if user.username == 'admin' and user.role == 1:  # admin 拥有所有权限
                    # permission_dict, menu_list = init_permission(user.username, is_super=True)  # 获取权限列表与菜单列表
                # else:
                    # permission_dict, menu_list = init_permission(user.username)     # 初始化权限和菜单
                # request.session[settings.INIT_PERMISSION] = permission_dict
                # request.session[settings.INIT_MENU] = menu_list
                # event_log(user, 1, '用户 [{}] 登陆成功'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return redirect(reverse('users:index'))  # 一切正确，则跳转到首页
            else:
                error_message = '密码错误!'
                # event_log(user, 3, '用户 [{}] 密码错误'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return render(request, 'login.html', locals())
        else:
            # event_log(None, 3, '登陆表单验证错误', request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return render(request, 'login.html', locals())
    return render(request, 'login.html')


# @ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def logout(request):
    if not request.session.get('islogin', None):
        return redirect(reverse('users:login'))
    try:
        user = UserProfile.objects.get(id=int(request.session.get('userid')))
        user.last_login_time = datetime.datetime.today()
        user.save()
        request.session.flush()     # 清除所有后包括django-admin登陆状态也会被清除
    except:
        return redirect(reverse('users:login'))
    # event_log(user, 2, '用户 [{}] 退出'.format(user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
    return redirect(reverse('users:login'))


class Registered(View):
    TEMPLATE = 'registered.html'

    def get(self, request):
        return render(request, self.TEMPLATE)

    def post(self, request):
        user = UserProfile()
        username = request.POST.get('username')
        user.username = username
        user.nick_name = request.POST.get('nickname')
        user.email = request.POST.get('email')
        user.password = hash_code(request.POST.get('passwd'))
        user.role = 1
        try:
            user.save()  # save user info
            kube = create_this_namespace(username)
            mkdir(username)  # mkdir user volume path
        except Exception as err:
            print(err)
            return JsonResponse({"status": 104, "error": err}, safe=False)
        return JsonResponse({"status": 200, "error": 'success', "kube": kube}, safe=False)


@login_required
def profile(request):
    '''展示个人资料'''
    # user = request.user
    # return render(request, 'users/u_profile.html', {'user': user})
    img = UserProfile.objects.get(username=request.session.get('username', None)).avatar
    nickname = request.session.get('nickname', None)
    role = request.session.get('role', None)
    page = '个人信息'
    return render(request, 'users/profile.html', locals())


# @login_required
def change_profile(request):
    '''更新个人资料'''
    if request.method == 'POST':
        # instance参数表示用model实例来初始化表单，这样就可以达到通过表单来更新数据
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # 添加一条信息，表单验证成功就重定向到个人信息页面
            messages.add_message(request, messages.SUCCESS, '个人信息更新成功！')
            return redirect('users:profile')
    else:
        # 不是POST请求就返回空表单
        form = ProfileForm(instance=request.user)

    return render(request, 'users/change_profile.html', context={'form': form})


def index(request):
    username = request.session.get('username', None)
    img = UserProfile.objects.get(username=username).avatar
    nickname = request.session.get('nickname', None)
    role = request.session.get('role', None)
    page = '首页'
    return render(request, 'users/index.html', locals())


# 异步跨域信息
def bash_info(request):

    func = request.GET.get("callback")

    img = str(settings.MEDIA_URL) + str(UserProfile.objects.get(id='3').avatar)
    nickname = request.session.get('nickname', None)
    role = request.session.get('role', None)
    data = {'img': img, 'nickname': nickname, 'role': role}
    return HttpResponse("%s('%s')" % (func, json.dumps(data)))
    # return JsonResponse(data, safe=False)


