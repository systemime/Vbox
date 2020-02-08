from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
from django.views.generic import View
from django.db.models import Q
from tools.k8s import KubeApi
from tools.tool import get_deploy_name
from tools.logs import event_log

from Vbox import celery_app

from users.models import UserProfile
from selectos.models import Systemos

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


@celery_app.task
def create_deployment(namespace, VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH, request):
    """
    异步任务，不能保证程序执行顺序
    先创建dep，查询数据库状态，存在则修改pod状态，不存在则暂时写入缓存，等待入库验证创建状态查询
    :param kwargs:
    :return:
    """
    task = KubeApi(namespace)
    info = task.create_deployment(VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH)
    print(info[0])
    key = DEPNAME + '_active'
    try:  # 得到创建结果，查询数据库数据存在，修改pod状态
        active = Systemos.objects.get(
            Q(user_id=str(namespace)) & Q(deployment=str(DEPNAME))
        )
        if not info[0]:
            active.active_status = 2
            active.save()
        else:
            active.active_status = 1
            active.save()
    except Exception as err:  # 得到创建结果，查询数据库数据不存在，写入缓存
        print("数据暂时未写入，pod状态写入缓存, 错误信息：" + str(err))
        if not info[0]:
            cache.set(key, 2, None)  # 创建该容器创建失败缓存，不过期
        else:
            cache.set(key, 1, None)
        print("缓存内容" + str(cache.get(key)))
    if not info[0]:  # 创建错误
        event_log.delay(namespace, 1, 10, '[{}] 创建容器 {} 失败'.format(namespace, DEPNAME), request.META.get('REMOTE_ADDR', None),
                        request.META.get('HTTP_USER_AGENT', None), info)
    else:
        event_log.delay(namespace, 1, 9, '[{}] 创建容器 {} 成功'.format(namespace, DEPNAME), request.META.get('REMOTE_ADDR', None),
                        request.META.get('HTTP_USER_AGENT', None), info)


@celery_app.task
def delete_deployment(request, namespace, dep_name):
    task = KubeApi(namespace)
    key_delete = dep_name + '_del'
    try:
        Systemos.objects.get(deployment=dep_name).delete()
        pod_num = UserProfile.objects.get(username=request.session.get('username', None))
        pod_num.pod_num = pod_num.pod_num - 1
        pod_num.save()
        cache.get_or_set(key_delete, pod_num.pod_num, None)
        event_log.delay(request.session.get('nickname', None), 1, 11,
                        '[{}] 删除容器 {} 数据成功'.format(request.session.get('nickname', None), dep_name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        dep_name)
    except Exception as err:
        event_log.delay(request.session.get('nickname', None), 1, 11,
                        '[{}] 删除容器 {} 数据失败'.format(request.session.get('nickname', None), dep_name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        str(err))
    info = task.delete_deployment(dep_name)
    if not info[0]:
        event_log.delay(request.session.get('nickname', None), 1, 11, '[{}] 删除容器失败'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        info)
    else:
        event_log.delay(request.session.get('nickname', None), 1, 11, '[{}] 删除容器成功'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        info)


@celery_app.task
def save_deployment_info(request, **kwargs):
    """
    读取缓存中该dep创建状态，存在直接写入数据库，不存在标注 0 正在生成
    :param kwargs:
    :return:
    """
    key = kwargs['deployment'] + '_active'
    key_pod_num = kwargs['deployment'] + '_pod_num'
    try:
        status = int(cache.get(key))
        print("获取缓存内容，缓存值为 %s" % status)
        cache.delete(key)
    except Exception as err:
        status = 0
        print("dep创建中，先写入数据库...，错误信息：%s" % err)
    try:
        # 创建新的容器表
        Systemos.objects.create(
            user_id=kwargs['user_id'],
            deployment=kwargs['deployment'],
            version=kwargs['version'],
            labels=kwargs['labels'],
            create_time=kwargs['create_time'],
            # storage=kwargs['storage'],  # 默认为5G，暂时无调整计划
            active_status=status,
            os=kwargs['os'],
            cpus=kwargs['cpus'],
            ram=kwargs['ram'],
            language=kwargs['language'],
            database=kwargs['database'],
            port=kwargs['port'],
            use_time=kwargs['use_time'],
            namespace=kwargs['namespace']
        )
        # 用户容器数量 +1
        pod_num = UserProfile.objects.get(username=kwargs['namespace'])
        pod_num.pod_num = pod_num.pod_num + 1
        pod_num.save()
        cache.get_or_set(key_pod_num, pod_num.pod_num, None)  # 添加bash侧边容器数量的缓存，仅在存入数据库成功时存入
        event_log.delay(kwargs['namespace'], 1, 9,
                        '[{}] 创建容器 {} 成功，数据录入成功'.format(kwargs['namespace'], kwargs['deployment']),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        kwargs['deployment'])
    except Exception as err:
        event_log.delay(kwargs['namespace'], 1, 9,
                        '[{}] 创建容器 {} 成功，数据未录入'.format(kwargs['namespace'], kwargs['deployment']),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        str(err))
        print("创建deployment时数据库存入失败 %s" % err)



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
        create_deployment(namespace, VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH, request)
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
    key_pod_num = str(request.session.get('username', None)) + '_pod_num'
    num = cache.get(key_pod_num)
    if not num:
        func = request.GET.get("getpodsum")
        data = {'sum': Systemos.objects.filter(namespace=request.session.get('username', None)).count()}
    else:
        data = {'sum': num}
    return HttpResponse("%s('%s')" % (func, json.dumps(data)))

