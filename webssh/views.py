from django.shortcuts import render
from django.http import JsonResponse
from tools.k8s import KubeApi
from selectos import models
from tools.tool import login_required
from tools.logs import event_log

# Create your views here.


@login_required
def web_ssh(request):
    """
    create web shh
    usernmae == namespace
    label == deployment[:10]
    :param request:
    :return: pod name
    """
    namespace = request.session.get('username', None)
    kub = KubeApi(namespace)
    try:
        label = models.Systemos.objects.get(id=request.GET.get("dep_id")).labels
    except Exception as err:
        event_log.delay(request.session.get('nickname', None), 1, 12,
                        '[{}] 建立ssh连接失败'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        '未查询到label' + str(err))
        return JsonResponse({"status": "参数错误", "error": "参数不存在！"})
    # print(label)
    state, data = kub.get_deployment_pod(label)  # 执行状态 / 信息
    if not state:
        event_log.delay(request.session.get('nickname', None), 1, 12,
                        '[{}] 建立ssh连接失败'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        'kubernetes查询pod信息失败' + str(data))
        return JsonResponse({"status": "发生错误", "error": data}, safe=False)
    else:
        pod_name = data.items[0].metadata.name  # data.items包含了所有的pod信息，为一个list列表
        event_log.delay(request.session.get('nickname', None), 1, 12,
                        '[{}] 建立ssh连接成功'.format(request.session.get('nickname', None)),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        '' + str(data))
        return render(request, 'webssh/ssh.html', {"name": pod_name, "namespace": namespace})


