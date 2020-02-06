from django.shortcuts import render
from django.http import JsonResponse
from tools.k8s import KubeApi
from tools.logs import event_log
from selectos.models import Systemos
from tools.tool import login_required
# Create your views here.


@login_required
def terminal(request, pod_id):
    """
    建立web guacamole连接
    :param request:
    :param pod_id: pod的id，便于查找对应虚拟IP, service 仅用于云平台部署时做服务发现
    :return: 链接页面或错误提示
    """
    error_message = '参数错误'
    try:
        host = Systemos.objects.get(id=pod_id)
    except Exception as err:
        event_log.delay(request.session.get('nickname', None), 1, 14,
                        '[{}] 建立vnc连接失败'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        '未查询到对应pod信息 ' + str(err))
        return JsonResponse({"status": "参数错误", "error": "参数不存在！"})
    namespace = host.namespace
    kub = KubeApi(namespace)
    state, data = kub.get_deployment_pod(host.labels)
    state, data = kub.get_this_pod_info(data.items[0].metadata.name)
    hostip = data.status.pod_ip
    print(hostip)
    if not hostip:
        event_log.delay(request.session.get('nickname', None), 1, 14,
                        '[{}] 建立vnc连接失败'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        '未查询到pod具体信息,host ip为空 ' + str(data))
        return JsonResponse({"code": 406, "err": "虚拟主机不存在"})
    else:
        event_log.delay(request.session.get('nickname', None), 1, 14,
                        '[{}] 建立vnc连接成功'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        '' + str(data))
        return render(request, 'webguacamole/guacamole.html', locals())


