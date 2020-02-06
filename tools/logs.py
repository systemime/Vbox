from users.models import UserLog
from Vbox import celery_app


@celery_app.task(ignore_result=True)
def event_log(user, log_type, event_type, detail, address, useragent, other_info):

    UserLog.objects.create(
        user=user,
        role=log_type,
        event_type=event_type,
        detail=detail,
        address=address,
        useragent=useragent,
        other=other_info  # 系统/错误信息，请求头部信息
    )

