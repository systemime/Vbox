# -*- coding: utf-8 -*-
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack  # 使用django自带auth认证获取信息
from channels.sessions import SessionMiddlewareStack  # 从session中获取信息
import webssh.routing
import webguacamole.routing

application = ProtocolTypeRouter({
    'websocket': SessionMiddlewareStack(  # 选择中间件
        URLRouter(
            # re_path(r'^pod/(?P<name>\w+)', SSHConsumer),
            webssh.routing.websocket_urlpatterns + webguacamole.routing.websocket_urlpatterns  # 导入app中websocket路由
        )
    ),
})

