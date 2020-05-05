from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from guacamole.client import GuacamoleClient
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
from tornado.websocket import WebSocketHandler
import os, sys, datetime, jwt
import asyncio
import aiomysql
from aiomysql import create_pool
from tools.k8s import KubeApi

define('port', type=int, help="run on the given port", default=60015)


class ChatHandler(WebSocketHandler):

    users = set()  # 用来存放在线用户的容器

    async def open(self, *args):
        self.users.add(self)  # 建立连接后添加用户到容器中
        token = self.get_argument("token", '').replace('_', '.')
        token = bytes(token, encoding="utf8")
        try:
            auth_info = jwt.decode(token, settings.SECRET_KEY, issuer='Vbox_guacd', algorithms='HS256')  # 解密，校验签名
        except Exception as err:
            print(err)
        pool = await aiomysql.create_pool(
            host='127.0.0.1', port=3306, user='root', password='Admin@2488.m', db='Vbox', charset='utf8')
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select * from django_session")
                value = await cur.fetchone()
                if str(auth_info.get('data')["session_key"]) in value:
                    print("查询成功")
        pool.close()
        await pool.wait_closed()
        for u in self.users:  # 向已在线用户发送消息
            u.write_message(u"[%s]-[%s]-进入聊天室" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def on_message(self, message):
        for u in self.users:  # 向在线用户广播消息
            u.write_message(u"[%s]-[%s]-说：%s" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))

    def on_close(self):
        self.users.remove(self) # 用户关闭连接后从容器中移除用户
        for u in self.users:
            u.write_message(u"[%s]-[%s]-离开聊天室" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求


class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        # print(request.session.get('nickname', None))
        self.write('Hello from tornado')
        print("--------->> %s" % settings.PASSWD_TOKEN)
        try:
            self.guacamoleclient = GuacamoleClient(
                settings.GUACD.get('172.17.0.2'),
                settings.GUACD.get('4822'),
                settings.GUACD.get('60'),
            )
            KubeApi('systemime')
        except Exception as err:
            print("失败了，别试了")


def main():
    parse_command_line()
    os.environ['DJANGO_SETTINGS_MODULE'] = 'Vbox.settings'
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/Vbox')

    django_wsgi_app = get_wsgi_application()
    wsgi_django_container = tornado.wsgi.WSGIContainer(django_wsgi_app)
    tornado_app = tornado.web.Application(
        [
            ('/hello-tornado', HelloHandler),
            # (r'/chat', ChatHandler),
            (r'/chat', ChatHandler),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_django_container)),
        ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
