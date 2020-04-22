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
def create_deployment(namespace, VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH, use_time, request):
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
        # print("数据暂时未写入，pod状态写入缓存, 错误信息：" + str(err))
        if not info[0]:
            cache.set(key, 2, None)  # 创建该容器创建失败缓存，不过期
        else:
            cache.set(key, 1, None)
        # print("缓存内容" + str(cache.get(key)))
    if not info[0]:  # 创建错误
        event_log.delay(namespace, 1, 10, '[{}] 创建容器 [{}] 失败'.format(namespace, DEPNAME), request.META.get('REMOTE_ADDR', None),
                        request.META.get('HTTP_USER_AGENT', None), info)
    else:
        create_timing(namespace, DEPNAME, use_time)  # 创建删除计划
        event_log.delay(namespace, 1, 9, '[{}] 创建容器 [{}] 成功'.format(namespace, DEPNAME), request.META.get('REMOTE_ADDR', None),
                        request.META.get('HTTP_USER_AGENT', None), info)


@app.task
def save_deployment_info(request, **kwargs):
    """
    读取缓存中该dep创建状态，存在直接写入数据库，不存在标注 0 正在生成
    :param kwargs:
    :return:
    """
    key = kwargs['deployment'] + '_active'
    key_pod_num = kwargs['user_id'] + '_pod_num'
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
        cache.set(key_pod_num, pod_num.pod_num, None)  # 添加bash侧边容器数量的缓存，仅在存入数据库成功时存入
        event_log.delay(kwargs['namespace'], 1, 9,
                        '[{}] 创建容器 [{}] 成功，数据录入成功'.format(kwargs['namespace'], kwargs['deployment']),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        kwargs['deployment'])
    except Exception as err:
        event_log.delay(kwargs['namespace'], 1, 9,
                        '[{}] 创建容器 [{}] 成功，数据未录入，纳入删除计划'.format(kwargs['namespace'], kwargs['deployment']),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        str(err))
        # 异常数据记录,celery定时任务删除
        ExceptDep.objects.create(
            namespace=request.session.get('username', None),
            deployment=kwargs['deployment'],
            cpus=kwargs['cpus'],
            ram=kwargs['ram'],
        )
        print("创建deployment时数据库存入失败 %s" % err)


@app.task
def delete_deployment(request, namespace, dep_name):
    task = KubeApi(namespace)
    key_pod_num = namespace + '_pod_num'
    try:
        Systemos.objects.get(deployment=dep_name).delete()
        pod_num = UserProfile.objects.get(username=request.session.get('username', None))
        pod_num.pod_num = pod_num.pod_num - 1
        pod_num.save()
        cache.set(key_pod_num, pod_num.pod_num, None)  # 当前容器数量
        event_log.delay(request.session.get('nickname', None), 1, 11,
                        '[{}] 删除容器 [{}] 数据成功'.format(request.session.get('nickname', None), dep_name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        dep_name)
    except Exception as err:  # 可能存在错误, 自动删除任务已执行,用户网页未刷新,执行了删除操作
        event_log.delay(request.session.get('nickname', None), 1, 11,
                        '[{}] 删除容器 [{}] 数据失败'.format(request.session.get('nickname', None), dep_name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        str(err))
    info = task.delete_deployment(dep_name)
    if not info[0]:
        event_log.delay(request.session.get('nickname', None), 1, 11,
                        '[{}] 删除 [{}] 容器失败'.format(request.session.get('nickname', None), dep_name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        info)
    else:
        event_log.delay(request.session.get('nickname', None), 1, 11,
                        '[{}] 删除 [{}] 容器成功'.format(request.session.get('nickname', None), dep_name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None),
                        info)
    try:  # 关闭自动删除计划
        periodic_task = PeriodicTask.objects.filter(name__contains=dep_name)  # field lookup 查询
        periodic_task.delete()
        event_log.delay('Admin', 0, 11, '[成功]针对用户 [{}] 容器 [{}] 的删除计划'.format(namespace, dep_name),
                        '清除关闭计划操作成功', '清除关闭计划操作成功', str(periodic_task))
    except Exception as err:
        event_log.delay('Admin', 0, 11, '[失败]针对用户 [{}] 容器 [{}] 的删除计划'.format(namespace, dep_name),
                        '清除关闭计划操作失败', '清除关闭计划操作失败', str(err))


@app.task
def regular_kill():
    """
    定期清除异常主机及数据
    :return:
    """
    print("开始执行删除异常主机任务....")
    except_info = ExceptDep.objects.all().order_by("namespace")
    except_user = set()
    if not except_info:
        pass
    else:
        num = except_info.count()
        except_name = except_info.first().namespace
        except_user.add(except_name)
        kube = KubeApi(except_name)
        for except_dep in except_info:
            if except_dep.namespace == except_name:
                kube.delete_deployment(except_dep.deployment)
            else:
                kube = KubeApi(except_dep.namespace)
                except_name = except_dep.namespace
                except_user.add(except_name)
                kube.delete_deployment(except_dep.deployment)
        except_info.delete()
        event_log.delay('Admin', 0, 11, '本次删除异常主机共计 [{}] 个'.format(num),
                        '定期任务', '定期任务', str(except_user))


@app.task
def timing_del_pod(namespace, deployment):
    """
    动态主机计时删除计划
    """
    task = KubeApi(namespace)
    key_pod_num = namespace + '_pod_num'
    try:
        Systemos.objects.get(deployment=deployment).delete()
        pod_num = UserProfile.objects.get(username=namespace)
        pod_num.pod_num = pod_num.pod_num - 1
        pod_num.save()
        cache.set(key_pod_num, pod_num.pod_num, None)
        event_log.delay('Admin', 0, 11,
                        '[Admin] 删除用户 [{}] 过期容器 [{}] 数据成功'.format(namespace, deployment),
                        '定时任务', '定时任务', '')
    except Exception as err:  # 错误类型: 数据存在错误, 容器已被删除, 定时任务没有被有效清理
        event_log.delay('Admin', 0, 11,
                        '[Admin] 删除用户 [{}] 过期容器 [{}] 数据失败'.format(namespace, deployment),
                        '定时任务', '定时任务', str(err))
    info = task.delete_deployment(deployment)
    if not info[0]:
        event_log.delay('Admin', 0, 11, '[Admin] 删除用户 [{}] 过期容器 [{}] 失败'.format(namespace, deployment),
                        '定时任务', '定时任务', info)
    else:
        event_log.delay('Admin', 0, 11, '[Admin] 删除用户 [{}] 过期容器 [{}] 成功'.format(namespace, deployment),
                        '定时任务', '定时任务', info)
    try:
        # 这里即时数据为空也会返回空列表, 该任务执行完成后, 下面的内容就是传说中的我删我自己......
        periodic_task = PeriodicTask.objects.filter(name__contains=deployment)  # field lookup 查询
        periodic_task.delete()
        event_log.delay('Admin', 0, 11, '[完成]清除针对用户 [{}] 的容器 [{}] 的删除计划'.format(namespace, deployment),
                        '删除计划执行完成', '删除计划执行完成', str(periodic_task))
    except Exception as err:
        event_log.delay('Admin', 0, 11, '[错误]针对用户 [{}] 的容器 [{}] 的删除计划删除失败'.format(namespace, deployment),
                        '删除计划执行完成', '删除计划执行完成', str(err))


def create_timing(namespace, deployment, use_time):
    """该函数创建成功后触发, 30分钟后过期
    通过django_celery_beat模块向表django_celery_beat_periodictask中动态添加新的定时任务
    djang-celery-beat 会自动检测执行任务并执行
    :param namespace:
    :param deployment:
    :param use_time:  用户选择的时长
    :return:
    """
    # 添加时间间隔
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=use_time,  # 多久一次
        period=IntervalSchedule.HOURS,
    )
    PeriodicTask.objects.create(
        interval=schedule,
        name='[create_timing_delete_task]' + deployment,  # 任务数据库的主键, 不能重复
        task='selectos.tasks.timing_del_pod',
        args=(json.dumps([namespace, deployment])),
        # kwargs=json.dumps({'be_careful': True,}),
        expires=datetime.utcnow() + timedelta(minutes=(int(use_time) * 60 + 5)),  # 过期时间,时区bug使用utc时间,目前好像不需要
        # queue='timing_queue',  # 后面三个不用指定,依赖于设置中的路由即可,指定则任务无效
        # exchange='timing_queue',
        # routing_key='timing_router'
    )
    event_log.delay('Admin', 0, 11, '[创建]针对用户 [{}] 的容器 [{}] 的删除计划'.format(namespace, deployment),
                    '成功创建删除计划', '成功创建删除计划', '成功')
    # periodic_task表, enabled属性 = False暂时关闭这个任务, 无save方法,只有update update_or_create方法
    #     # 测试enabled属性未知bug根本无效, 代码中应立即删除
    # IntervalSchedule.DAYS HOURS MINUTES SECONDS MICROSECONDS

