# -*- coding: utf-8 -*-
from channels.generic.websocket import WebsocketConsumer
from tools.k8s import KubeApi, K8SStreamThread
from tools.logs import ssh_log, event_log


class SSHConsumer(WebsocketConsumer):
    def connect(self):
        """
        连接建立时触发
        :param 从链接的cookies中获取信息
        :return:
        """
        self.name = self.scope["url_route"]["kwargs"]["name"]  # pod name
        self.namespace = self.scope["url_route"]["kwargs"]["namespace"]
        self.cols = self.scope["url_route"]["kwargs"]["cols"]
        self.rows = self.scope["url_route"]["kwargs"]["rows"]
        self.message = ''

        # kube exec
        kube = KubeApi(self.namespace)
        self.stream = kube.pod_exec(self.name, cols=self.cols, rows=self.rows)
        kub_stream = K8SStreamThread(self, self.stream)  # 使用新的线程维持链接
        kub_stream.start()

        self.accept()

    def disconnect(self, close_code):
        """
        连接关闭时触发
        :param close_code: 1000在ssh内输入exit，1001手动关闭标签页
        :return:
        """
        if close_code == 1001:
            self.stream.write_stdin('exit\r')
            nickname = self.scope["session"].get('nickname', None)  # 从头文件里获取，？？？那我还保持为空干啥
            # REMOTE_ADDR = self.scope['headers']
            # HTTP_USER_AGENT = self.scope['headers']
            event_log.delay(nickname, 1, 13, '[{}] 关闭ssh链接'.format(nickname),
                            '', '', str(self.scope['headers']))

    def receive(self, text_data):
        """
        收到消息后触发
        :param text_data: 单字节
        """
        if chr(13) is text_data:
            if self.message == 'exit':
                nickname = self.scope["session"].get('nickname', None)
                event_log.delay(nickname, 1, 13, '[{}] 关闭ssh链接'.format(nickname),
                                '', '', str(self.scope['headers']))
            else:
                ssh_log(self.namespace, self.name, self.message)
                self.message = ''
        else:
            self.message += text_data
        self.stream.write_stdin(text_data)

