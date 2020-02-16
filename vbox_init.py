from django.core.cache import cache


cache.clear()

# 认证tokne
# APISERVER=$(kubectl config view --minify | grep server | cut -f 2- -d ":" | tr -d " ")
# Token=$(kubectl describe secret $(kubectl get secret -n kube-system | grep ^admin-user | awk '{print $1}') -n kube-system | grep -E '^token'| awk '{print $2}')

# ansible
# echo "1" > /proc/sys/net/ipv4/ip_forward
# echo "1" >/proc/sys/net/bridge/bridge-nf-call-iptables