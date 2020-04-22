from django.core.cache import cache
from tools import tool


cache.clear()  # 清除残余缓存
tool.user_cache()  # 获取所有用户username

# 认证tokne
# APISERVER=$(kubectl config view --minify | grep server | cut -f 2- -d ":" | tr -d " ")
# Token=$(kubectl describe secret $(kubectl get secret -n kube-system | grep ^admin-user | awk '{print $1}') -n kube-system | grep -E '^token'| awk '{print $2}')

# ansible
# echo "1" > /proc/sys/net/ipv4/ip_forward
# echo "1" >/proc/sys/net/bridge/bridge-nf-call-iptables

# celery启动
# 启动服务: nohup celery -A Vbox worker -l info -P eventlet > logs/celery.log 2>&1 &
# 定时:    nohup celery -A Vbox beat -l info > logs/celery_beat.log 2>&1 &
# ---------------------------------------------------------------------------
# 全新测试时,重启redis或删除全部cache, cache.clear()
# cd /home/soul/Desktop/Vbox
# pip install eventlet  # 引入协程
# 不引用协程
# nohup celery -A Vbox worker -l info > logs/celery.log 2>&1 &
# 合并
# celery -A Vbox worker -b -l info
