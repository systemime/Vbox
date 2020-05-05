from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.conf import settings
import datetime
import jwt
from tools.k8s import KubeApi
from tools.logs import event_log
from selectos.models import Systemos
# from tools.tool import login_required
# Create your views here.


# @login_required
def terminal(request, pod_id):
    """
    建立web guacamole连接
    :param request:
    :param pod_id: pod的id，便于查找对应虚拟IP, service 仅用于云平台部署时做服务发现
    :return: 链接页面或错误提示
    """
    # error_message = '参数错误'
    # try:
    #     host = Systemos.objects.get(id=pod_id)
    # except Exception as err:
    #     event_log.delay(request.session.get('nickname', None), 1, 14,
    #                     '[{}] 建立vnc连接失败'.format(request.session.get('nickname', None)),
    #                     request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
    #                     '未查询到对应pod信息 ' + str(err))
    #     return JsonResponse({"status": "403", "error": "参数不存在！"})
    #
    # namespace = host.namespace
    # kube = KubeApi(namespace)
    # state, data = kube.get_deployment_pod(host.labels)
    # state, data = kube.get_this_pod_info(data.items[0].metadata.name)
    # hostip = data.status.pod_ip
    # print(hostip)
    #
    # key = settings.SECRET_KEY  # 加密密钥
    # session_key = request.session.session_key  # session id -> str
    # print(session_key)
    # pyload = {
    #     'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=4),  # 过期时间, 对比要求utc时间
    #     'iat': datetime.datetime.utcnow(),  # 开始时间
    #     'iss': 'Vbox_guacd',  # 签名
    #     'data': {
    #         'host_id': pod_id,
    #         'username': namespace,
    #         'host_ip': hostip,
    #         'session_key': session_key
    #     }
    # }
    # token = jwt.encode(pyload, key, algorithm='HS256')
    # print(token)  # byes类型
    # encoded_token = token.decode('utf-8')
    # encoded = encoded_token.replace('.', '_')  # token的.换成_
    #
    # return render(request, 'talk.html', locals())

    # if not hostip:
    #     event_log.delay(request.session.get('nickname', None), 1, 14,
    #                     '[{}] 建立vnc连接失败'.format(request.session.get('nickname', None)),
    #                     request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
    #                     '未查询到pod具体信息,host ip为空 ' + str(data))
    #     return JsonResponse({"code": 406, "err": "虚拟主机不存在"})
    # else:
    #     event_log.delay(request.session.get('nickname', None), 1, 14,
    #                     '[{}] 建立vnc连接成功'.format(request.session.get('nickname', None)),
    #                     request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
    #                     '' + str(data))
    #     return render(request, 'webguacamole/guacamole.html', locals())

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


