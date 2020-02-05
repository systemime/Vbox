from django.shortcuts import render
from django.http import JsonResponse
from tools.k8s import KubeApi
from selectos.models import Systemos
from tools.tool import login_required
# Create your views here.


@login_required
def terminal(request, pod_id):
    """
    返回连接界面
    :param request:
    :param pod_id: pod的id，便于查找对应虚拟IP
    :return: 链接页面或错误提示
    """
    error_message = '参数错误'
    try:
        host = Systemos.objects.get(id=pod_id)
    except Exception as err:
        return JsonResponse({"status": "参数错误", "error": "参数不存在！"})
    namespace = host.namespace
    kub = KubeApi(namespace)
    state, data = kub.get_deployment_pod(host.labels)
    state, data = kub.get_this_pod_info(data.items[0].metadata.name)
    hostip = data.status.pod_ip
    print(hostip)
    if not pod_id:
        return JsonResponse({"code": 406, "err": error_message})
    else:
        return render(request, 'webguacamole/guacamole.html', locals())


