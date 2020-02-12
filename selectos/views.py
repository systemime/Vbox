from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
from django.views.generic import View
from tools.tool import get_deploy_name

from Vbox import celery_app
from .tasks import *

from users.models import UserProfile
from selectos.models import Systemos, ExceptDep

from tools.tool import login_required
# 对类视图使用装饰器需要使用这个方法
from django.utils.decorators import method_decorator

# from django.views.decorators.cache import cache_page  # 缓存装饰器
# @cache_page(5)  # 部分数据需要实时更新，所以还是使用redis作为缓存服务器，cache方法实现缓存
from django.core.cache import cache  # 操作缓存 clear() 清空所有缓存
# from django.views.decorators.cache import cache_control
# @cache_control(private=True)  # 私有缓存标识
# @cache_control(must_revalidate=True, max_age=3600)  # 每次访问均验证缓存，最长保存3600s


@celery_app.task
def delete_this_namespace(name):
    task = KubeApi(name)
    info = task.delete_user_namespace()
    print(info)


@method_decorator(login_required, name='dispatch')  # dispatch代表全部方法
class Selectos(View):

    # @method_decorator(cache_page(5))  # 对单个方法加装饰器
    def get(self, request):  # 这里需要实时更新所以不加入缓存了，后期添加访问限制
        data = {}
        data['array'] = range(1, 5)
        data['os_list'] = list(Systemos.os_list)
        data['language_list'] = list(Systemos.language_list)
        data['database_list'] = list(Systemos.database_list)
        img = UserProfile.objects.get(username=request.session.get('username', None)).avatar
        nickname = request.session.get('nickname', None)
        role = request.session.get('role', None)
        page = '容器信息'
        container_info = self.container_list(request)
        nickname = request.session.get('nickname', None)
        event_log.delay(nickname, 1, 20, '[{}] 访问容器信息页面'.format(nickname),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        str(request.headers))
        return render(request, 'selectos/inspiration.html', locals())

    def container_list(self, request):
        username = str(request.session.get('username', None))
        container_info = Systemos.objects.filter(user=username, active_status=1)
        return container_info

    def post(self, request):
        imgname_list = {
            'Ubuntu': 'dorowu/ubuntu-desktop-lxde-vnc',  # 18.04
            'Centos': 'centos:7',
            'Ubuntu 16.04': 'dorowu/ubuntu-desktop-lxde-vnc',
            'Ubuntu 14.04': 'dorowu/ubuntu-desktop-lxde-vnc',
        }
        cpu_limit = {  # CPU time
            '1': '500m',  # 1/2
            '2': '1000m',
            '3': '1500m',
            '4': '2000m',
        }
        os = request.POST.get('os')
        language = request.POST.get('language')
        database = request.POST.get('database')
        use_time = request.POST.get('use_time')

        namespace = request.session.get('username', None)
        VERSION = 'apps/v1'
        DEPNAME, create_time = get_deploy_name()
        IMGNAME = imgname_list[os]

        # readUint32: unexpected character: \\ufffd, error found in #10 byte of ...|erPort\\": \\"59999\\"}],
        # 单引号，必须正整形，未知bug
        port = request.POST.get('port')
        if not port:
            port = 64444
        PORTS = int(port)

        DIR = '/home/soul/tools/' + str(namespace)
        CPUS = cpu_limit[str(request.POST.get('cpus'))]  # 单位不同
        MEMORY = str(request.POST.get('memory')) + 'Mi'
        EPH = '5Gi'

        # 创建异步创建任务
        create_deployment(namespace, VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH, use_time, request)
        # 异步保存数据
        save_deployment_info(
            request, user_id=namespace, deployment=DEPNAME, version=VERSION, labels=DEPNAME[:25],
            create_time=create_time, os=os, cpus=request.POST.get('cpus'),
            ram=request.POST.get('memory'), language=language, database=database, port=port,
            use_time=use_time, namespace=namespace
        )
        return JsonResponse({"status": 200, "error": "数据提交成功，正在生成"}, safe=False)


@login_required
def delete_user_deployment(request):
    """
    删除主机
    :param request: deployment id
    :return: 删除结果
    """
    dep_id = request.GET.get('dep_id')
    namespace = request.session.get('username', None)
    try:  # 立即标注删除
        dep_name = Systemos.objects.get(id=dep_id).deployment
        active = Systemos.objects.get(
            Q(user_id=str(namespace)) & Q(deployment=str(dep_name))
        )
        active.active_status = 3
        active.save()
        delete_deployment(request, namespace, dep_name)
    except Exception as err:
        event_log.delay(request.session.get('nickname', None), 1, 11,
                        '[{}] 主机参数不存在'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        str(err))
    return JsonResponse({"status": 200, "error": "删除请求已提交"}, safe=False)


@login_required
# @cache_page(10)  # 10秒缓存
def pod_num(request):
    """
    虚拟主机数量
    :param request:
    :return: 主机数量
    """
    key_pod_num = str(request.session.get(  'username', None)) + '_pod_num'
    num = cache.get(key_pod_num)  # 不存在就是None
    if not num:
        fun_name = request.GET.get("getpodsum")
        data = {'sum': Systemos.objects.filter(namespace=request.session.get('username', None)).count()}
    else:
        # print("缓存存在: %s" % num)
        fun_name = request.GET.get("getpodsum")
        data = {'sum': num}
    return HttpResponse("%s('%s')" % (fun_name, json.dumps(data)))

