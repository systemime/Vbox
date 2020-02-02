from channels.generic.websocket import WebsocketConsumer
from tools.k8s import KubeApi
from threading import Thread


class K8SStreamThread(Thread):
    """
    调用k8s中exec接口实现链接
    """
    def __init__(self, websocket, container_stream):
        Thread.__init__(self)
        self.websocket = websocket
        self.stream = container_stream

    def run(self):
        while self.stream.is_open():
            if self.stream.peek_stdout():
                stdout = self.stream.read_stdout()
                self.websocket.send(stdout)

            if self.stream.peek_stderr():
                stderr = self.stream.read_stderr()
                self.websocket.send(stderr)
        else:
            self.websocket.close()


class SSHConsumer(WebsocketConsumer):
    def connect(self):
        """
        连接建立时触发
        :return:
        """
        # 从链接的cookies中获取信息
        self.name = self.scope["url_route"]["kwargs"]["name"]
        self.namespace = self.scope["url_route"]["kwargs"]["namespace"]

        self.cols = self.scope["url_route"]["kwargs"]["cols"]
        self.rows = self.scope["url_route"]["kwargs"]["rows"]

        # kube exec
        kube = KubeApi(self.namespace)
        self.stream = kube.pod_exec(self.name, cols=self.cols, rows=self.rows)
        kub_stream = K8SStreamThread(self, self.stream)
        kub_stream.start()


        self.accept()

    def disconnect(self, close_code):
        """
        连接建立时触发
        :param close_code:
        :return:
        """
        self.stream.write_stdin('exit\r')

    def receive(self, text_data):
        """
        收到消息后触发
        :param text_data:
        :return:
        """
        self.stream.write_stdin(text_data)