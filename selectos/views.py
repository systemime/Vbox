from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
from django.views.generic import View
from tools.k8s import KubeApi
from tools.tool import get_deploy_name

from Vbox import celery_app

from users.models import UserProfile
from selectos.models import Systemos

from tools.tool import login_required
# 对类视图使用装饰器需要使用这个方法
from django.utils.decorators import method_decorator


@celery_app.task
def delete_this_namespace(name):
    task = KubeApi(name)
    info = task.delete_user_namespace()
    print(info)


@celery_app.task
def create_deployment(namespace, VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH):
    task = KubeApi(namespace)
    info = task.create_deployment(VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH)
    print(info)

@celery_app.task
def delete_deployment(namespace, dep_name):
    task = KubeApi(namespace)
    info = task.delete_deployment(dep_name)
    print(info)


@method_decorator(login_required, name='dispatch')  # dispatch代表全部方法
class Selectos(View):

    # @method_decorator(login_required)  # 对单个方法加装饰器
    def get(self, request):
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
        return render(request, 'selectos/inspiration.html', locals())

    def container_list(self, request):
        username = str(request.session.get('username', None))
        container_info = Systemos.objects.filter(user=username)
        return container_info

    def post(self, request):
        container = Systemos()

        imgname_list = {
            'Ubuntu': 'dorowu/ubuntu-desktop-lxde-vnc',
            'Centos': 'centos:7',
        }
        cpu_limit = {
            '1': '500m',
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
        CPUS = cpu_limit[str(request.POST.get('cpus'))]
        MEMORY = str(request.POST.get('memory')) + 'Mi'
        EPH = '5Gi'
        try:
            print(namespace, VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH)
            create_deployment(namespace, VERSION, DEPNAME,
                              IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH)
        except Exception as err:
            print("创建错误" + err)
            return JsonResponse({"status": 1304, "error": err}, safe=False)

        try:
            container.user_id = namespace
            container.deployment = DEPNAME
            container.version = VERSION
            container.labels = DEPNAME[:25]
            container.create_time = create_time
            # container.storage = 5  # 默认为5G，暂时无调整计划
            container.os = os
            container.cpus = request.POST.get('cpus')
            container.ram = request.POST.get('memory')
            container.language = language
            container.database = database
            container.port = port
            container.use_time = use_time
            container.namespace = namespace
            container.save()
            pod_num = UserProfile.objects.get(username=namespace)
            pod_num.pod_num = pod_num.pod_num + 1
            pod_num.save()
            # user_pod_num.pod_num = container.objects.get(username=request.session.get('username', None)).pod_num + 1
        except Exception as err:
            print(err)
            return JsonResponse({"status": "创建成功", "error": "字段存储失败"}, safe=False)

        return JsonResponse({"status": 200, "error": "生成成功"}, safe=False)

@login_required
def delete_user_deployment(request):
    dep_id = request.GET.get('dep_id')
    dep_name = Systemos.objects.get(id=dep_id).deployment
    print(dep_name)
    try:
        Systemos.objects.get(id=dep_id).delete()
        pod_num = UserProfile.objects.get(username=request.session.get('username', None))
        pod_num.pod_num = pod_num.pod_num - 1
        pod_num.save()
        delete_deployment(namespace=request.session.get('username', None), dep_name=dep_name)
    except Exception as err:
        return JsonResponse({"status": "删除失败", "error": err}, safe=False)
    return JsonResponse({"status": 200, "error": "删除成功"}, safe=False)


@login_required
def pod_num(request):
    func = request.GET.get("getpodsum")
    data = {'sum': Systemos.objects.filter(namespace=request.session.get('username', None)).count()}
    return HttpResponse("%s('%s')" % (func, json.dumps(data)))

