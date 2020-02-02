"""
routing功能类似django中url路由功能
"""
from django.urls import re_path
from tools.consumers import SSHConsumer

websocket_urlpatterns = [
    re_path(r'^pod/(?P<name>[\w-]+)/(?P<namespace>\w+)/(?P<cols>\d+)/(?P<rows>\d+)$', SSHConsumer),  # name获取
]
