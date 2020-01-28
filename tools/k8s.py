from kubernetes import client, config
from kubernetes.stream import stream
from kubernetes.client.rest import ApiException


class KubeApi:
    def __init__(self, namespace='default'):
        """
        初始化api，获取当前/将创建namespace，并建立连接
        :param namespace:
        """
        config.load_kube_config("/home/soul/tools/kubeconfig.yaml")  # path need confirmation
        self.namespace = namespace

    def create_user_namespace(self):
        """
        创建用户的namespace
        :return:
        """
        api_instance = client.CoreV1Api()
        body = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=self.namespace)
        )
        try:
            r = api_instance.create_namespace(
                body=body
            )
            return True, "Namespace created: %s" % r
        except Exception as e:
            return False, 'Namespace created: ' + str(e)

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

    def create_deployment(self, VERSION, DEPNAME, IMGNAME, PORT, DIR):
        """
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
                selector={'matchLabels': {'app': DEPNAME}},
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": DEPNAME}),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            name=DEPNAME,
                            image=IMGNAME,
                            # env=[{"name": "ENVT", "value": ENVT}, {"name": "PROJ", "value": PROJ}],
                            ports=[client.V1ContainerPort(container_port=PORT)],
                            volume_mounts=[client.V1VolumeMount(mount_path='/home/', name='v'+DEPNAME)],
                        )],
                        volumes=[client.V1Volume(
                            name='v' + DEPNAME,
                            host_path=[client.V1HostPathVolumeSource(path=DIR)]
                        )]
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

    def delete_deployment(self, RAND):
        api_instance = client.AppsV1Api()
        body = client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5)

        try:
            r = api_instance.delete_namespaced_deployment(
                namespace=self.namespace,
                name=RAND,
                body=body
            )

            return True, "Deployment deleted. %s" % r
        except Exception as e:
            return False, 'Deployment deleted: ' + str(e)

    def edit_deployment(self, **kwargs):
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
        k8s_core_v1 = client.CoreV1Api()
        resp = k8s_core_v1.delete_namespaced_pod(namespace=self.namespace, name=pod_name)

    def get_this_pod_info(self, pod_name):
        """
        获取某个pod的详细信息
        :param pod_name:
        :return:
        """
        api_instance = client.CoreV1Api()
        resp = api_instance.read_namespaced_pod(namespace=self.namespace, name=pod_name)

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

    def test_pods_connect(self, podname, namespace, command, container=None):
        """
        功能不明确
        """
        api_instance = client.CoreV1Api()
        if stream(api_instance.connect_get_namespaced_pod_exec, podname, namespace, command=command,
                  container=container,
                  stderr=True, stdin=False,
                  stdout=True, tty=False):
            return True
        else:
            return False

    def get_pods_exec(self, podname, namespace, command, container=None):
        """
        获得ssh链接函数
        :param podname:
        :param namespace:
        :param command:
        :param container:
        :return:
        """
        api_instance = client.CoreV1Api()
        if container:
            rest = stream(api_instance.connect_get_namespaced_pod_exec, podname, namespace, command=command,
                          container=container,
                          stderr=True, stdin=False,
                          stdout=True, tty=False)
        else:
            rest = stream(api_instance.connect_get_namespaced_pod_exec, podname, namespace, command=command,
                          stderr=True, stdin=False,
                          stdout=True, tty=False)
        return rest

    def get_all_namespace_service(self):
        api_instance = client.CoreV1Api()
        ret = api_instance.list_service_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s \t%s \t%s \t%s \t%s \n" % (
                i.kind, i.metadata.namespace, i.metadata.name, i.spec.cluster_ip, i.spec.ports)
            )

    def create_service(self, service_name=''):
        k8s_api_obj = client.CoreV1Api()
        namespace = self.namespace
        if service_name=='':
            service_name=self.namespace
        body = {'apiVersion': 'v1', 'kind': 'Service',
                'metadata': {'name': service_name, 'labels': {'app': 'nginx'}},
                'spec': {'ports': [{'port': 80, 'targetPort': 80}], 'selector': {'app': 'nginx'}}}
        try:
            api_response = k8s_api_obj.create_namespaced_service(namespace, body)
            print(api_response)
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)

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








