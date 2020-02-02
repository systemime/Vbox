from django.shortcuts import render
from django.http import JsonResponse
from tools.k8s import KubeApi
from selectos import models

# Create your views here.


def web_terminal(request):
    """
    usernmae == namespace
    label == deployment[:10]
    :param request:
    :return: pod name
    """
    namespace = request.session.get('username', None)
    kub = KubeApi(namespace)
    label = models.Systemos.objects.get(id=request.GET.get("dep_id")).labels
    print(label)
    state, data = kub.get_deployment_pod(label)  # 执行状态 / 信息
    if not state:
        return JsonResponse({"status": "发生错误", "error": data}, safe=False)
    else:
        pod_name = data.items[0].metadata.name  # data.items包含了所有的pod信息，为一个list列表
        return render(request, 'webssh/ssh.html', {"name": pod_name, "namespace": namespace})


