# FastVbox
测试需要安装guacad服务，主要功能已完成，其他功能暂不更新

### 开启celery  

> nohup celery -A Vbox worker -l info -P eventlet > logs/celery_worker.log 2>&1 &  
> nohup celery -A Vbox beat -l info > logs/celery_beat.log 2>&1 &
  - install
    ```
    pip install celery
    pip install redis
    # 或者是直接：pip install "celery[redis]"
    pip install mysqlclient
    # 非必须，默认Celery是不保存任务结果的，如果想要查看任务的结果并且保存到数据库中，就必须安装该依赖，如果不想保存到数据库的话，也可以使用Redis来进行保存
    # pip install django-celery-results
    # if use
    # INSTALLED_APPS = (
    #     ...,
    #     'django_celery_results',
    # )
    # python manage.py migrate django_celery_results
    ```

### 缓存
Redis

  - session
  - 容器创建缓存读写
  - bash页面头像等

### 消息队列
  - RabbitMQ
    要在较新的Ubuntu版本上安装它非常简单：
    ```
    apt-get install -y erlang
    apt-get install rabbitmq-server
    ```

  - 然后启用并启动RabbitMQ服务：
    ```
    systemctl enable rabbitmq-server
    systemctl start rabbitmq-server
    ```

  - 检查状态以确保一切运行顺利：
    ```
    systemctl status rabbitmq-server
    ```
