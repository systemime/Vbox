from celery import task
from Vbox.celery import app
from django.db.models import Q
from tools.k8s import KubeApi
from django.core.cache import cache
from tools.logs import event_log

from users.models import UserProfile
from selectos.models import Systemos, ExceptDep
# 定时一次性任务
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule  # 操作动态任务计划数据库
from datetime import datetime, timedelta  # timedelta,设置时间间隔, 两者配合实现日期相加


@app.task
def task_monitor():
    """
    定期获取监控数据 CPU/MEM
    """
    kube = KubeApi()
    try:
        start_n, nodes = kube.get_target_monitor_dict('nodes')  # 各个节点监控
        start_p, pods = kube.get_target_monitor_dict('pods')  # 各个pod监控
    except Exception as err:
        pass
    node = json.loads(nodes)["items"]
    pod = json.loads(pods)["items"]
    event_log.delay('Admin', 0, 11, '本次删除异常主机共计 [{}] 个'.format(num),
                    '定期任务', '定期任务', str(except_user))

# pod example
# {
# 'metadata': {
# 	'name': 'kube-proxy-tlxj7',
#     'namespace': 'kube-system',
#     'selfLink': '/apis/metrics.k8s.io/v1beta1/namespaces/kube-system/pods/kube-proxy-tlxj7',
#     'creationTimestamp': '2020-02-17T11:01:33Z'
# },
# 'timestamp': '2020-02-17T11:00:54Z',
# 'window': '30s',
# 'containers': [{
# 	'name': 'kube-proxy',
#     'usage': {
# 		'cpu': '3452323n', 'memory': '24616Ki'
# 	}
# }]
# },
# node example
# [{
# 'metadata': {
# 	'name': 'master',
# 	'selfLink': '/apis/metrics.k8s.io/v1beta1/nodes/master',
# 	'creationTimestamp': '2020-02-17T13:12:39Z'
# },
# 'timestamp': '2020-02-17T13:12:05Z',
# 'window': '30s',
# 'usage': {
# 	'cpu': '296885624n',
# 	'memory': '2488384Ki'
# }
# }]


