from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
from django.views.generic import View
from selectos import models
from tools.k8s import KubeApi
from Vbox import celery_app

from users.models import UserProfile

from tools.tool import login_required
# 对类视图使用装饰器需要使用这个方法
from django.utils.decorators import method_decorator


@celery_app.task
def delete_this_namespace(name):
    task = KubeApi(name)
    info = task.delete_user_namespace()
    print(info)


@method_decorator(login_required, name='dispatch')  # dispatch代表全部方法
class Selectos(View):

    # @method_decorator(login_required)  # 对单个方法加装饰器
    def get(self, request):
        data = {}
        data['array'] = range(1, 5)
        data['os_list'] = list(models.Systemos.os_list)
        data['proxy_list'] = list(models.Systemos.proxy_list)
        data['language_list'] = list(models.Systemos.language_list)
        data['database_list'] = list(models.Systemos.database_list)
        data['port'] = range(30000, 32000)
        img = UserProfile.objects.get(id='3').avatar
        nickname = request.session.get('nickname', None)
        role = request.session.get('role', None)
        page = '容器信息'
        return render(request, 'selectos/inspiration.html', locals())

    def post(self, request):
        print(request.POST.get('os'))
        # namespace = request.POST.get('namespace', '')
        # create_this_namespace(namespace)

        return JsonResponse({"status": 200, "error": "生成成功"}, safe=False)


def delete_user_pod(request):
    return JsonResponse({"status": 200, "error": "删除成功"}, safe=False)







