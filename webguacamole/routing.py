# -*- coding: utf-8 -*-
"""
routing功能类似django中url路由功能
"""
from django.urls import path
from webguacamole.websocket_layer import WebGuacamole

websocket_urlpatterns = [
    path('ws/webguacamole/', WebGuacamole),
]
