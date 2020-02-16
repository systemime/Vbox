from threading import Thread
from django.conf import settings
from asgiref.sync import async_to_sync
import time
import traceback
from tools.tool import gen_rand_char, res
from guacamole.client import GuacamoleClient
import sys
import os


class Client:
    def __init__(self, websocker):
        self.websocker = websocker

        self.start_time = time.time()
        self.last_save_time = self.start_time

        tmp_date1 = time.strftime("%Y-%m-%d", time.localtime(int(self.start_time)))
        tmp_date2 = time.strftime("%Y%m%d%H%M%S", time.localtime(int(self.start_time)))

        if not os.path.isdir(os.path.join(settings.RECORD_ROOT, tmp_date1)):
            os.makedirs(os.path.join(settings.RECORD_ROOT, tmp_date1))
        self.res_file = settings.RECORD_DIR + '/' + tmp_date1 + '/' + 'webguacamole_' + \
                        tmp_date2 + '_' + gen_rand_char(16) + '.txt'
        self.res = []  # 信息流
        self.guacamoleclient = None

    def connect(self, protocol, hostname, port, username, password, width, height, dpi):
        try:
            # 获取服务端信息建立连接，超时时间30
            self.guacamoleclient = GuacamoleClient(
                settings.GUACD.get('host'),
                settings.GUACD.get('port'),
                settings.GUACD.get('timeout'),
            )
            if protocol == 'vnc':  # vnc 登陆不需要账号
                # 通过握手与Guacamole guacd服务器建立连接
                # 默认参数 width=1024, height=768, dpi=96
                self.guacamoleclient.handshake(
                    protocol=protocol,
                    hostname=hostname,
                    port=port,
                    password=password,  # 实际上为vnc密码，无密码vnc可使用通用密码
                    width=width,
                    height=height,
                    dpi=dpi,
                )
            elif protocol == 'rdp':  # 暂不支持rdp链接，保留做升级
                self.guacamoleclient.handshake(
                    protocol=protocol,
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    width=width,
                    height=height,
                    dpi=dpi,
                )
            Thread(target=self.websocket_to_django).start()
        except Exception:
            self.websocker.close(3001)

    def django_to_guacd(self, data):
        try:
            self.guacamoleclient.send(data)
        except Exception:
            self.close()

    def websocket_to_django(self):
        try:
            while True:
                # time.sleep(0.0001)  # 链接需要时间，暂缓一下
                # 可以使用select来控制变成非阻塞,这里必须等待
                # 没有数据到来时会阻塞，获取这部分数据
                data = self.guacamoleclient.receive()  # 此位置该模块本身存在bug,与程序无关
                if not data:
                    return
                if self.websocker.send_flag == 0:  # 普通用户登录
                    self.websocker.send(data)
                elif self.websocker.send_flag == 1:  # 管理员登录时
                    async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                        "type": "group.message",
                        "text": data,
                    })
                # 连接信息添加到res
                self.res.append(data)
                # 每六十秒或字节数超过数据大于两千条或内存占用超过2MB时
                if len(self.res) > 2000 or int(time.time() - self.last_save_time) > 60 or \
                        sys.getsizeof(self.res) > 2097152:
                    tmp = list(self.res)
                    # 清空连接信息
                    self.res = []
                    # 重置上次保存时间
                    self.last_save_time = time.time()
                    # delay() 为 apply_async() 的快捷使用, 详细见博客笔记，celery不立刻执行该函数，获取返回值res.id，
                    res.delay(self.res_file, tmp, False)  # 返回值已屏蔽
                    # res = res.delay(self.res_file, tmp, False)
                    # id = res.id
                    # from celery.result import AsyncResult
                    # res = AsyncResult("62051878-ca77-4895-a61f-6f9525681347")  # 参数为task id
                    # res.result/res.state
        except Exception:
            print(traceback.format_exc())  # 输出详细，类似print_exc()，但是返回的是字符串
            if self.websocker.send_flag == 0:
                self.websocker.send('0.;')
            elif self.websocker.send_flag == 1:
                async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                    "type": "group.message",
                    "text": '0.;',
                })
        finally:
            # 信道关闭时关闭websocket连接（guacd连接自动关闭）
            self.close()

    def close(self):
        self.websocker.close()
        self.guacamoleclient.close()

    def shell(self, data):
        self.django_to_guacd(data)
