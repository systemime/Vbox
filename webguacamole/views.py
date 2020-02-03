from django.shortcuts import render
from util.tool import post_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from tools.k8s import KubeApi
from selectos.models import Systemos
# Create your views here.


# @post_required
def terminal(request, pod_id):
    error_message = '456789456'
    host = Systemos.objects.get(id=pod_id)
    namespace = host.namespace
    kub = KubeApi(namespace)
    state, data = kub.get_deployment_pod(host.labels)
    state, data = kub.get_this_pod_info(data.items[0].metadata.name)
    hostip = data.status.pod_ip
    print(hostip)
    print("=======================================")
    if not pod_id:
        return JsonResponse({"code": 406, "err": error_message})
    else:
        return render(request, 'webguacamole/guacamole.html', locals())


