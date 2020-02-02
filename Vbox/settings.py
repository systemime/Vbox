"""
Django settings for Vbox project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l4&k#gn_tzzcovy9fd+^-ia42g#u-5)m$)ba&mykokp&@_hlia'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 跨域app注册
    'corsheaders',
    # django-allauth必须安装的app
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 第三方账号相关，根据需求添加
    'allauth.socialaccount.providers.weibo',
    'allauth.socialaccount.providers.github',
    # bootstrap 表单样式
    'crispy_forms',
    # websocket
    'channels',
    # 自定义app
    'users',
    'selectos',
    'file',
    'webssh',
]

# 配置表单插件使用的样式
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 跨域
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 跨域设置
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = []
CORS_ALLOW_METHODS = [
    ' DELETE ',
    ' GET ',
    ' OPTIONS ',
    ' PATCH ',
    ' POST ',
    ' PUT ',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_CREDENTIALS = True

X_FRAME_OPTIONS = 'ALLOWALL'

SECURE_HSTS_SECONDS = 3600

ROOT_URLCONF = 'Vbox.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # 图片显示相关
            ],
        },
    },
]

WSGI_APPLICATION = 'Vbox.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Vbox',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '192.168.221.133',
        'PORT': '3306',
    }
}

redis_setting = {
    'host': '127.0.0.1',
    'port': 6379,
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # blog是项目名，media是约定成俗的文件夹名
MEDIA_URL = "/media/"      # 跟STATIC_URL类似，指定用户可以通过这个路径找到文件

# 用户加密密钥, 第一次设置后切勿再随意更改
PASSWD_TOKEN = '__66711__Ops__devops'

# session 如果在此期间未做任何操作，则退出， django 本身要么设置固定时间，要么关闭浏览器失效
CUSTOM_SESSION_EXIPRY_TIME = 60 * 120    # 30 分钟

# 终端过期时间，最好小于等于 CUSTOM_SESSION_EXIPRY_TIME
CUSTOM_TERMINAL_EXIPRY_TIME = 60 * 120

# websocket channels设置
# 指定ASGI的路由地址， channels运行于ASGI协议上一种异步服务网关接口协议
ASGI_APPLICATION = 'Vbox.routing.application'

# 使用redis作为channel layer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(redis_setting['host'], redis_setting['port'])],
        },
    },
}

# Celery application definition 异步任务设置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYD_MAX_TASKS_PER_CHILD = 10
CELERYD_LOG_FILE = os.path.join(BASE_DIR, "logs", "celery_work.log")
CELERYBEAT_LOG_FILE = os.path.join(BASE_DIR, "logs", "celery_beat.log")


# from datetime import timedelta
# # 这里是定时任务的配置
# CELERY_BEAT_SCHEDULE = {
#     'task_method': {  # 随便起的名字
#         'task': 'app.tasks.method_name',  # app 下的tasks.py文件中的方法名
#         'schedule': timedelta(seconds=10),  # 名字为task_method的定时任务, 每10秒执行一次
#     },
# }

# celery -A linux_news worker -l info -B -f /path/to/log
# -A 表示app所在的目录，-B表示启动celery beat运行定时任务。
#
# 启动celery：celery worker -A tasks --loglevel=info
# 同时启动works 和beat：celery -B -A ProjectName worker --loglevel=info
#
# celery -A proj worker -l info

 # django-allauth相关设置
AUTHENTICATION_BACKENDS = (
      # django admin所使用的用户登录与django-allauth无关
      'django.contrib.auth.backends.ModelBackend',
      # allauth 身份验证
      'allauth.account.auth_backends.AuthenticationBackend',
)

# smtp 服务器地址
EMAIL_HOST = "smtp.qq.com"
# 默认端口25，若请求超时可尝试465
EMAIL_PORT = 465
# 用户名
EMAIL_HOST_USER = "cchandler@qq.com"
# 邮箱代理授权码（不是邮箱密码）
EMAIL_HOST_PASSWORD = "erqlgnfdeuefbcad"
# 是否使用了SSL 或者TLS（两者选其一）
# EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
# 发送人
EMAIL_FROM = "cchandler@qq.com"
# 默认显示的发送人，（邮箱地址必须与发送人一致），不设置的话django默认使用的webmaster@localhost
DEFAULT_FROM_EMAIL = "Vbox 注册 <cchandler@qq.com>"

# app django.contrib.sites需要的设置
SITE_ID = 1
# 要求用户注册时必须填写email
ACCOUNT_EMAIL_REQUIRED = True
# 必须验证邮箱
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# 邮件发送后的冷却时间(以秒为单位)
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 180
# 邮箱确认邮件的截止日期(天数)
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
# 指定要使用的登录方法(用户名、电子邮件地址或两者之一)
ACCOUNT_AUTHENTICATION_METHOD = "username"
# 登录尝试失败的次数
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
# 从上次失败的登录尝试，用户被禁止尝试登录的持续时间
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 60
# 更改或设置密码后是否自动退出
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
# 更改为True，用户将在重置密码后自动登录
ACCOUNT_LOGIN_ON_PASSWORD_RESET = False
# 控制会话的生命周期，可选项还有: "False" 和 "True"
ACCOUNT_SESSION_REMEMBER = None
# 用户注册时是否需要用户输入两遍密码
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
# 用户不能使用的用户名列表
ACCOUNT_USERNAME_BLACKLIST = ['systemime', 'root', 'name', 'system']
# 加强电子邮件地址的唯一性
ACCOUNT_UNIQUE_EMAIL = True
# 用户名允许的最小长度的整数
ACCOUNT_USERNAME_MIN_LENGTH = 4
# 使用从社交账号提供者检索的字段(如用户名、邮件)来绕过注册表单
SOCIALACCOUNT_AUTO_SIGNUP = True

# 设置登录后跳转链接
LOGIN_REDIRECT_URL = "/accounts/profile/"
# 设置退出登录后跳转链接
ACCOUNT_LOGOUT_REDIRECT_URL = "http://192.168.221.133:60013/users/login"
# 用户登出是否需要确认确认(True表示直接退出，不用确认；False表示需要确认)
ACCOUNT_LOGOUT_ON_GET = False


# 指定user类使用自定义用户模型
AUTH_USER_MODEL = 'users.UserProfile'

# django-ratelimit 限制页面访问频率，超过则返回 403
# None 表示无限制，具体见 https://django-ratelimit.readthedocs.io/en/stable/rates.html
# RATELIMIT_LOGIN = None
RATELIMIT_LOGIN = '600/30s'
RATELIMIT_NOLOGIN = '20/30s'

