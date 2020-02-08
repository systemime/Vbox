# FastVbox
毕设项目

#### 开启celery  

> nohup celery -A Vbox worker -l info > logs/celery.log 2>&1 &

#### 缓存
Redis

  - session
  - 容器创建缓存读写
  - bash页面头像等
