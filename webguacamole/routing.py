# -*- coding: utf-8 -*-
"""
routing功能类似django中url路由功能
"""
from django.urls import re_path, path
from webguacamole.websocket_layer import WebGuacamole

websocket_urlpatterns = [
    path('ws/webguacamole/', WebGuacamole),
]
# websocket_urlpatterns = [
#     re_path(r'^pod/(?P<name>[\w-]+)/(?P<namespace>\w+)/(?P<cols>\d+)/(?P<rows>\d+)$', SSHConsumer),  # name获取
# ]
