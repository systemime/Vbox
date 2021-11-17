from kubernetes import client, config
from kubernetes.stream import stream
from kubernetes.client import ApiClient
from kubernetes.client.rest import ApiException
import json
import threading
from threading import Thread
from django.conf import settings


class KubeApi:
    """
    api初始化方法：
        client.CoreV1Api()  # 常用方法
        client.AppsV1Api()  # 更细致

    封装前请仔细阅读对应源码，同一函数不同初始化方法返回结果不同
    """

    _instance_lock = threading.Lock()

    def __init__(self, namespace='default'):
        """
        初始化api，获取目标namespace，并建立连接
        :param namespace:
        """
        # 简单尝试可以使用这种方法，修改一下目录
        # config.load_kube_config("/home/soul/tools/kubeconfig.yaml")  # path need confirmation
        configuration = client.Configuration()
        configuration.host = settings.APISERVER  # settings/base.py中配置该字符串，我的你们用不了，一个k8s申请一个
        configuration.verify_ssl = False  # 不验证加密
        configuration.api_key = {"authorization": "Bearer " + settings.TOKEN}
        client.Configuration.set_default(configuration)
        self.namespace = namespace

    def __new__(cls, *args, **kwargs):
        if not hasattr(KubeApi, "_instance"):
            with KubeApi._instance_lock:
                if not hasattr(KubeApi, "_instance"):
                    KubeApi._instance = super(KubeApi, cls).__new__(cls, *args, **kwargs)
        return KubeApi._instance

    def create_user_namespace(self):
        """
        创建用户的namespace
        :return:
        """
        api_instance = client.CoreV1Api()
        body = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=self.namespace),
        )
        try:
            r = api_instance.create_namespace(
                body=body
            )
            res = self.create_resourcequota()
            return True, "Namespace created: %s \t %s" % (r, res)
        except Exception as e:
            return False, 'Namespace created: ' + str(e)

    def create_namespace_limit(self):
        """
        创建namespace的资源申请范围限制
        :return:
        """
        api_instance = client.CoreV1Api()
        body = {
            "apiVersion": "v1",
            "kind": "LimitRange",
            "metadata": {
                "name": "limit-test"
            },
            "spec": {
                "limits": [{
                    "type": "Pod",  # 对Pod中所有容器资源总和进行限制
                    "max": {
                        "cpu": "8000m",
                        "memory": "6144Mi"
                    },
                    "min": {
                        "cpu": "100m",
                        "memory": "512Mi"
                    },
                    "maxLimitRequestRatio": {
                        "cpu": 5,
                        "memory": 5
                    }
                }, {
                    "type": "Container",  # 对Pod中所有容器资源进行限制
                    "max": {
                        "cpu": "4000m",
                        "memory": "2048Mi"
                    },
                    "min": {
                        "cpu": "500m",
                        "memory": "512Mi"
                    },
                    "maxLimitRequestRatio": {
                        "cpu": 5,
                        "memory": 5
                    },
                    "default": {
                        "cpu": "4000m",
                        "memory": "2048Mi"
                    },
                    "defaultRequest": {
                        "cpu": "500m",
                        "memory": "512Mi"
                    }
                }]
            }
        }
        try:
            api_instance.create_namespaced_limit_range(namespace=self.namespace, body=body)
            return True
        except:
            return False

    def create_resourcequota(self):
        """
        创建namespace资源限制，配合函数双重限制
        最多4个cpu， 2G内存用量，5GB硬盘用量
        综合不超过4个cpu，4G内存
        :return:
        """
        api_instance = client.CoreV1Api()
        body = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {
                "name": "compute-resources"
            },
            "spec": {
                "hard": {
                    "limits.cpu": "3",
                    "limits.memory": "5Gi",  # 总使用量
                    "pods": "4",
                    "requests.cpu": "2",
                    "requests.memory": "4Gi",  # 总请求量
                    "requests.storage": "20Gi"
                }
            }
        }
        try:
            r = api_instance.create_namespaced_resource_quota(namespace=self.namespace, body=body)
            return True, "resourcequota created: %s" % r
        except Exception as err:
            return False, "resourcequota created: %s" % err

    def create_service(self, service_name=''):
        """
        创建用户namespace网络
        :param service_name:
        :return:
        """
        k8s_api_obj = client.CoreV1Api()
        namespace = self.namespace
        if service_name == '':
            service_name = self.namespace
        body = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': service_name,
                'labels': {'app': 'nginx'}
            },
            'spec': {
                'ports': [{'port': 80, 'targetPort': 80}],
                'selector': {'app': 'nginx'}
            }
        }
        try:
            api_response = k8s_api_obj.create_namespaced_service(namespace, body)
            print(api_response)
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)

    def delete_user_namespace(self):
        """
        删除用户同时，删除对应namespace
        :return:
        """
        api_instance = client.CoreV1Api()
        try:
            r = api_instance.delete_namespace(
                name=self.namespace
            )
            return True, "Namespace delete: %s" % r
        except Exception as e:
            return False, 'Namespace delete: ' + str(e)

    def create_deployment(self, VERSION, DEPNAME, IMGNAME, PORTS, DIR, CPUS, MEMORY, EPH):
        """
        kub.create_deployment('apps/v1','f6415217d83e0b7e50b81db896dbf0b6','nginx:1.14.0',80,'/home/soul/tools/test',1,'2048Mi','15Gi')
        :param VERSION: version
        :param DEPNAME: deployment name
        :param IMGNAME: image name
        :param PORT: port
        :param DIR: 外部路径
        :return: create deployment success or false info
        """
        api_instance = client.AppsV1Api()
        body = client.V1Deployment(
            api_version=VERSION,
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=DEPNAME),
            spec=client.V1DeploymentSpec(
                replicas=1,
                # selector指明哪个pod被管理，如果和deployment name混合相同，会造成未知错误
                # http://docs.kubernetes.org.cn/317.html
                selector={'matchLabels': {'app': DEPNAME[:25]}},
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": DEPNAME[:25]}),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            name=DEPNAME[:25],
                            image=IMGNAME,
                            # env=[{"name": "ENVT", "value": ENVT}, {"name": "PROJ", "value": PROJ}],
                            # ports=[client.V1ContainerPort(container_port=PORTS)],
                            ports=[{'containerPort': PORTS}],
                            # ports=PORTS,
                            resources={
                                "requests": {
                                    "cpu": CPUS,
                                    "memory": MEMORY,
                                    "ephemeral-storage": EPH
                                },
                                "limits": {
                                    "cpu": CPUS,
                                    "memory": MEMORY,
                                    "ephemeral-storage": "5Gi"
                                }
                            },
                            volume_mounts=[client.V1VolumeMount(mount_path='/opt/'+DEPNAME[:25], name='v'+DEPNAME[:25])],
                        )],
                        volumes=[{
                            "name": 'v'+DEPNAME[:25],
                            "hostPath": {"path": DIR}
                        }]
                    )
                ),
            )
        )

        try:
            r = api_instance.create_namespaced_deployment(
                namespace=self.namespace, body=body
            )
            return True, "Deployment created: %s" % r
        except Exception as e:
            return False, 'Deployment created: ' + str(e)

    def delete_deployment(self, DEPNAME):
        """
        注意！DEPNAME为空值时，默认删除该namespace下所有deployment！检查参数传递！
        :param DEPNAME:
        :return:
        """
        api_instance = client.AppsV1Api()
        body = client.V1DeleteOptions()
        try:
            r = api_instance.delete_namespaced_deployment(
                namespace=self.namespace,
                name=DEPNAME,
                body=body
            )

            return True, "Deployment deleted. %s" % r
        except Exception as e:
            return False, 'Deployment deleted: ' + str(e)

    def pod_exec(self, pod, rows=24, cols=80, container=""):
        api_instance = client.CoreV1Api()

        exec_command = [
            "/bin/sh",
            "-c",
            # 'export LINES=20; export COLUMNS=100; '  # 固定窗口大小
            'TERM=xterm-256color; export TERM; [ -x /bin/bash ] '
            '&& ([ -x /usr/bin/script ] '
            '&& /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) '
            '|| exec /bin/sh']

        cont_stream = stream(api_instance.connect_get_namespaced_pod_exec,
                             name=pod,
                             namespace=self.namespace,
                             container=container,
                             command=exec_command,
                             stderr=True, stdin=True,
                             stdout=True, tty=True,
                             _preload_content=False
                             )
        cont_stream.write_channel(4, json.dumps({"Height": int(rows), "Width": int(cols)}))
        return cont_stream

    def get_deployment_pod(self, RAND):
        """
        获取该deployment下pod信息，不够详细
        :param RAND: deployment的labels
        :return: result
        """
        api_instance = client.CoreV1Api()

        try:
            r = api_instance.list_namespaced_pod(
                namespace=self.namespace,
                label_selector="app=%s" % RAND
            )

            return True, r
        except Exception as err:
            return False, 'Get Deployment: %s' % err

    def get_target_monitor_dict(self, target):
        """
        :param target: nodes pods
        """
        api_client = ApiClient()
        try:
            ret_metrics = api_client.call_api('/apis/metrics.k8s.io/v1beta1/' + target,
                                              'GET', auth_settings=['BearerToken'],
                                              response_type='json', _preload_content=False)
            response = ret_metrics[0].data.decode('utf-8')
            return True, response
        except Exception as err:
            return False, str(err)

    def test_pods_connect(self, podname, namespace, command, container=None):
        """
        :return 返回pod链接成功
        """
        api_instance = client.CoreV1Api()
        if stream(api_instance.connect_get_namespaced_pod_exec, podname, namespace, command=command,
                  container=container,
                  stderr=True, stdin=False,
                  stdout=True, tty=False):
            return True
        else:
            return False

    def edit_deployment(self, *args):
        """
        提供环境变更按钮/配置edit_service使用
        :param kwargs:
        :return:
        """
        k8s_core_v1 = client.CoreV1Api()
        # 例子
        # old_resp = k8s_core_v1.read_namespaced_pod(namespace="default", name='nginx-pod')
        # old_resp.spec.containers[0].image = "nginx:alpine"
        # # 修改镜像
        # new_resp = k8s_core_v1.patch_namespaced_pod(namespace="default", name='nginx-pod', body=old_resp)
        # print(new_resp.spec.containers[0].image)

    def delete_pod(self, pod_name):
        """
        删除单个 pod
        :param pod_name:
        :return:
        """
        k8s_core_v1 = client.CoreV1Api()
        body = client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5  # 删除宽限值，0是立即删除
        )
        resp = k8s_core_v1.delete_namespaced_pod(namespace=self.namespace, name=pod_name)

    def get_this_deployment_info(self, dep_name):
        """
        获取某个deploy的信息，一般从数据库读出，配置好redis无压力
        :param dep_name:
        :return:
        """
        api_instance = client.AppsV1Api()
        try:
            resp = api_instance.read_namespaced_deployment(namespace=self.namespace, name=dep_name)

            return True, resp
        except Exception as err:
            return False, str(err)

    def get_this_pod_info(self, pod_name):
        """
        获取namespace下某个pod的详细信息
        :param pod_name:
        :return:
        """
        api_instance = client.CoreV1Api()
        try:
            resp = api_instance.read_namespaced_pod(namespace=self.namespace, name=pod_name)
            return True, resp
        except Exception as err:
            return False, err

    def get_podlist(self):
        """
        获取所有pod的详细信息
        :return:
        """
        api_instance = client.CoreV1Api()
        ret_pod = api_instance.list_namespaced_pod(namespace=self.namespace)
        return ret_pod

    def get_namespacelist(self):
        api_instance = client.CoreV1Api()
        ret_namespace = api_instance.list_namespace()
        return ret_namespace

    def get_all_namespace_service(self):
        api_instance = client.CoreV1Api()
        ret = api_instance.list_service_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s \t%s \t%s \t%s \t%s \n" % (
                i.kind, i.metadata.namespace, i.metadata.name, i.spec.cluster_ip, i.spec.ports)
            )

    def delete_service(self, service_name=''):
        k8s_api_obj = client.CoreV1Api()
        if service_name=='':
            name = self.namespace  # 要删除svc名称
        namespace = self.namespace  # 命名空间
        grace_period_seconds = 0  # 延迟时间,0立即删除
        # body = client.V1DeleteOptions()  # 删除选项
        try:
            api_response = k8s_api_obj.delete_namespaced_service(
                name, namespace, grace_period_seconds=grace_period_seconds)
            print(api_response)
        except ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespaced_service: %s\n" % e)

    def read_service(self, svc_name=""):
        """
        获得某个service的详细信息
        :param svc_name:
        :return:
        """
        api_instance = client.CoreV1Api()
        api_response = api_instance.read_namespaced_service(svc_name, self.namespace)
        return api_response

    # def create_service(self, file="service-nginx.yaml", namespace="default"):
    #     """
    #     为高级用户提供自定义生成方法,后期完成
    #     :param file:
    #     :param namespace:
    #     :return:
    #     """
    #     with open(path.join(path.dirname(__file__), file)) as f:
    #         dep = yaml.safe_load(f)
    #         api_response = self.Api_Instance.create_namespaced_service(namespace, body=dep)
    #         return api_response


class K8SStreamThread(Thread):
    """
    调用k8s中exec接口实现链接
    创建新线程维持链接
    """
    def __init__(self, websocket, container_stream):
        # 工作线程、工作队列、线程编号
        Thread.__init__(self)
        self.websocket = websocket
        self.stream = container_stream

    def run(self):
        # #重载threading类中的run()
        while self.stream.is_open():
            if self.stream.peek_stdout():
                stdout = self.stream.read_stdout()
                self.websocket.send(stdout)

            if self.stream.peek_stderr():
                stderr = self.stream.read_stderr()
                self.websocket.send(stderr)
        else:
            self.websocket.close()





