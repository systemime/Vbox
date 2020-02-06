from users.models import UserLog
from webssh.models import Logs_to_SSH
from Vbox import celery_app


@celery_app.task(ignore_result=True)
def event_log(user, log_type, event_type, detail, address, useragent, other_info):
    """
    用户操作日志记录
    :param user:
    :param log_type:
    :param event_type:
    :param detail:
    :param address:
    :param useragent:
    :param other_info:
    :return:
    """
    UserLog.objects.create(
        user=user,
        role=log_type,
        event_type=event_type,
        detail=detail,
        address=address,
        useragent=useragent,
        other=other_info  # 系统/错误信息，请求头部信息
    )


@celery_app.task
def ssh_log(user, pod_name, message):
    Logs_to_SSH.objects.create(
        user_id=user,
        pod_name=pod_name,
        command=message
    )

