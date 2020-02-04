from channels.generic.websocket import WebsocketConsumer

# from server.models import RemoteUserBindHost  # 导入主机类
from selectos.models import Systemos
# from webssh.models import TerminalSession  # 会话记录表，这是记录在线终端的

import django.utils.timezone as timezone

# 同步代码中使用channel layer的方法（包括send()、group_send()，group_add()等异步方法），都需要使用await，即使用装饰器asgiref.sync.async_to_sync
from asgiref.sync import async_to_sync
import platform
from guacamole.client import GuacamoleClient
from .guacamoleclient import Client

from django.http.request import QueryDict
# from webssh.tasks import celery_save_res_asciinema, celery_save_terminal_log  # 创建操作文件，写入日志表
from util.tool import gen_rand_char
from tools.k8s import KubeApi


class WebGuacamole(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 在HttpRequest对象中, GET和POST属性是django.http.QueryDict类的实例。
        # QueryDict类似字典的自定义类，用来处理单键对应多值的情况，实现所有标准的词典方法。还包括一些特有的方法：
        # QueryDict('a=1&a=2&c=3') < QueryDict: {'a': ['1', '2'], 'c': ['3']} >
        query_string = self.scope.get('query_string').decode()  # 请求参数
        guacamole_args = QueryDict(query_string=query_string, encoding='utf-8')

        self.hostid = int(guacamole_args.get('hostid'))  # 主机id

        self.host = Systemos.objects.get(id=self.hostid)
        self.namespace = self.host.namespace
        kub = KubeApi(self.namespace)
        state, data = kub.get_deployment_pod(self.host.labels)
        state, data = kub.get_this_pod_info(data.items[0].metadata.name)
        self.hostip = data.status.pod_ip

        self.remote_host = self.host  # 远程主机信息
        self.protocol = 'vnc'
        self.width = guacamole_args.get('width')  # 宽
        self.height = guacamole_args.get('height')  # 高
        self.dpi = guacamole_args.get('dpi')  # 分辨率
        self.session = None  # session
        self.start_time = timezone.now()  # 启动时间
        self.send_flag = 0  # 0 发送自身通道，1 发送 group 通道，作用为当管理员查看会话时，进入 group 通道
        self.group = 'session_' + gen_rand_char()  # 组名随机
        self.user_agent = None  # 登录端浏览器等信息
        self.guacamoleclient = None  # 客户端

    def connect(self):
        """
        连接建立
        :return:
        """
        self.accept('guacamole')
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)  # 加入组
        self.session = self.scope.get('session', None)  # 获取session

        # 登录状态查询
        if not self.session.get('islogin', None):  # 未登录直接断开 websocket 连接
            self.close(3001)

        # 获取主机信息
        # self.host 已经获取
        # self.remote_host = RemoteUserBindHost.objects.get(id=self.hostid)

        # 登录协议查询 vnc 登陆不需要账号
        # 这里需要从前/后端传入协议名称,或者默认vnc
        _type = 8  # web vnc

        # 建立连接
        self.guacamoleclient = Client(websocker=self)
        self.guacamoleclient.connect(
            protocol=self.protocol,  # 协议
            hostname=self.hostip,  # 主机ip， 这里从k8s查询
            port='5900',  # 主机端口， 默认5900
            username='root',  # 登录账号名称， 默认root
            password='123456',  # 登录账户密码，默认123456
            width=self.width,  # 宽
            height=self.height,  # 高
            dpi=self.dpi,  # 分辨率
        )

        # 获取登录端浏览器等信息
        # for i in self.scope['headers']:
        #     if i[0].decode('utf-8') == 'user-agent':  # 登录端浏览器等信息
        #         self.user_agent = i[1].decode('utf-8')
        #         break
        #
        # data = {
        #     'name': self.channel_name,  # 频道名称
        #     'group': self.group,  # 组
        #     'user': self.session.get('username'),  # 用户名
        #     'host': self.remote_host.ip,  # 主机ip
        #     'username': self.remote_host.remote_user.username,  # 登录账户名
        #     'protocol': self.protocol,  # 协议
        #     'port': self.remote_host.port,  # 端口
        #     'type': _type,  # 协议代码
        #     'address': self.scope['client'][0],  # clinet端信息
        #     'useragent': self.user_agent,  # 浏览器信息
        # }
        # 会话信息存入数据库
        # TerminalSession.objects.create(**data)

    def disconnect(self, close_code):
        """
        连接断开,
        :param close_code:
        :return:
        """
        try:
            # 使用异步方法, 关闭连接（（固定异步方法）（组名/连接名，连接名/连接信息））
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)
            if close_code != 3001:  # 已经关闭了，无需再次关闭
                self.guacamoleclient.close()
        except:
            pass
        finally:
            if self.guacamoleclient.res:
                try:
                    tmp = list(self.guacamoleclient.res)
                    self.guacamoleclient.res = []
                    if platform.system().lower() == 'linux':
                        pass
                        # 创建一个文件保存操作（内容没看懂）
                        # celery_save_res_asciinema.delay(
                        #     settings.MEDIA_ROOT + '/' + self.guacamoleclient.res_file, tmp, False
                        # )
                    else:
                        pass
                        # with open(settings.MEDIA_ROOT + '/' + self.guacamoleclient.res_file, 'a+') as f:
                        #     for line in tmp:
                        #         f.write('{}'.format(line))
                except:
                    pass

                try:
                    pass
                    # 保存操作日志
                    # if platform.system().lower() == 'linux':
                    #     celery_save_terminal_log.delay(
                    #         self.session.get('username'),
                    #         self.remote_host.hostname,
                    #         self.remote_host.ip,
                    #         self.remote_host.get_protocol_display(),
                    #         self.remote_host.port,
                    #         self.remote_host.remote_user.username,
                    #         '',
                    #         self.guacamoleclient.res_file,
                    #         self.scope['client'][0],
                    #         self.user_agent,
                    #         self.start_time,
                    #     )
                    # else:
                    #     terminal_log(
                    #         self.session.get('username'),
                    #         self.remote_host.hostname,
                    #         self.remote_host.ip,
                    #         self.remote_host.get_protocol_display(),
                    #         self.remote_host.port,
                    #         self.remote_host.remote_user.username,
                    #         '',
                    #         self.guacamoleclient.res_file,
                    #         self.scope['client'][0],
                    #         self.user_agent,
                    #         self.start_time,
                    #     )
                except:
                    pass

            # 查询这条连接信息并删除
            # TerminalSession.objects.filter(name=self.channel_name, group=self.group).delete()

    def receive(self, text_data=None, bytes_data=None):
        """
        消息传递
        :param text_data:
        :param bytes_data:
        :return:
        """
        self.guacamoleclient.shell(text_data)

    # 会话外使用 channels.layers 设置 type 为 group.message 调用此函数
    def group_message(self, data):
        try:
            self.send(data['text'])
        except BaseException:
            pass

    # 会话外使用 channels.layers 设置 type 为 close.message 调用此函数
    def close_message(self, data):
        try:
            self.close()
        except BaseException:
            pass

